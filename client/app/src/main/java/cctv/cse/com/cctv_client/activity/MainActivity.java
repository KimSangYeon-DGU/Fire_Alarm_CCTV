package cctv.cse.com.cctv_client.activity;

import android.app.ProgressDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.net.Uri;
import android.os.AsyncTask;
import android.support.annotation.NonNull;
import android.support.design.widget.BottomNavigationView;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.support.v7.widget.SwitchCompat;
import android.util.Base64;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.MenuItem;
import android.view.View;
import android.widget.CompoundButton;
import android.widget.ImageView;
import com.ceylonlabs.imageviewpopup.ImagePopup;
import com.google.firebase.iid.FirebaseInstanceId;
import org.json.JSONException;
import org.json.JSONObject;
import java.io.DataInput;
import java.io.DataInputStream;
import java.io.DataOutput;
import java.io.DataOutputStream;
import java.io.IOException;
import java.lang.ref.WeakReference;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

import cctv.cse.com.cctv_client.util.ConstantsUtil;
import cctv.cse.com.cctv_client.etc.Item;
import cctv.cse.com.cctv_client.R;
import cctv.cse.com.cctv_client.window.RecyclerPopupWindow;

public class MainActivity extends AppCompatActivity {

    private ImageView mIv_frame;
    private ImageView mIv_mark;
    private Bitmap mBtm_receive;
    private NetworkTask networkTask;

    private BottomNavigationView bottomNavigationView;
    private RecyclerPopupWindow recyclerPopupWindow;
    private JSONObject inJson;
    private JSONObject outJson;
    private boolean isConnected;
    private ImageView ivPopup;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main_land);
        String refreshedToken = FirebaseInstanceId.getInstance().getToken();
        //ivPopup = findViewById(R.id.iv_popup);
        ivPopup = new ImageView(this);
        Log.d("REGID",refreshedToken);
        try {
            init();
        } catch (JSONException e) {
            e.printStackTrace();
        }
        mIv_frame = findViewById(R.id.iv_frame);
        mIv_mark = findViewById(R.id.iv_mark);

        bottomNavigationView = findViewById(R.id.bnv_menu);

        final SwitchCompat switchCompat = findViewById(R.id.sc_connect);
        // Set default image on receive ImageView

        mIv_mark.setImageDrawable(getResources().getDrawable(R.drawable.stop));
        mIv_frame.setBackgroundColor(Color.WHITE);
        mIv_frame.setVisibility(View.INVISIBLE);
        mIv_mark.setVisibility(View.VISIBLE);

        isConnected  = false;

        switchCompat.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if (isChecked){
                    if (!isConnected) {
                        isConnected = true;
                        try {

                            mIv_mark.setVisibility(View.INVISIBLE);
                            mIv_frame.setVisibility(View.VISIBLE);
                            // initialize the worker
                            networkTask = new NetworkTask(
                                    MainActivity.this,
                                    ConstantsUtil.ip,
                                    ConstantsUtil.port
                            );

                            networkTask.execute();

                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    }
                }
                else{
                    isConnected = false;
                    networkTask = null;
                }
            }
        });

        bottomNavigationView.setOnNavigationItemSelectedListener(new BottomNavigationView.OnNavigationItemSelectedListener() {
            @Override
            public boolean onNavigationItemSelected(@NonNull MenuItem item) {
                switch (item.getItemId()) {
                    case R.id.bot_menu_home:
                        turnOnAndOffHD("off");
                        break;

                    case R.id.bot_menu_hd:
                        turnOnAndOffHD("on");
                        break;

                    case R.id.bot_menu_list:
                        turnOnAndOffHD("off");
                        switchCompat.setChecked(false);
                        showListDialog();
                        break;

                    case R.id.bot_menu_info:
                        turnOnAndOffHD("off");
                        switchCompat.setChecked(false);
                        showInfoDialog();
                        break;

                    case R.id.bot_menu_call:
                        // Turn off TCT socket stream.
                        turnOnAndOffHD("off");
                        String phone = "119";
                        Intent intent = new Intent(Intent.ACTION_DIAL, Uri.fromParts("tel", phone, null));
                        startActivity(intent);
                        break;
                }
                return true;
            }
        });

    }

    private void showFireImage(ImageView imageView, int width, int height) {
        final ImagePopup imagePopup = new ImagePopup(this);
        imagePopup.initiatePopup(imageView.getDrawable());
        imagePopup.setWindowWidth((int)(ConstantsUtil.displayWidth/1.5));
        imagePopup.setWindowHeight((int)(ConstantsUtil.displayHeight/1.5));
        imagePopup.viewPopup();
    }

    private void showListDialog(){
        final AlertDialog.Builder alertDialog = new AlertDialog.Builder(this, R.style.Theme_AppCompat_Light_Dialog_Alert);
        alertDialog.setMessage(R.string.conn_context)
                .setTitle(R.string.conn_name)
                .setPositiveButton("Yes", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        dialog.cancel();
                        DataTask infoDataTask = new DataTask(MainActivity.this, "CAM01", "log", "null");
                        infoDataTask.execute();
                    }
                })
                .setNegativeButton("No", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        dialog.cancel();
                    }
                })
                .setCancelable(false)
                .show();
    }

    private void showInfoDialog(){
        final AlertDialog.Builder alertDialog2 = new AlertDialog.Builder(this, R.style.Theme_AppCompat_Light_Dialog_Alert);
        alertDialog2.setMessage(R.string.conn_context)
                .setTitle(R.string.conn_name)
                .setPositiveButton("Yes", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        //loadInfoDataFromServer("CAM01");
                        dialog.cancel();
                        DataTask infoDataTask = new DataTask(MainActivity.this, "CAM01", "info", "null");
                        infoDataTask.execute();

                    }
                })
                .setNegativeButton("No", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        dialog.cancel();
                    }
                })
                .setCancelable(false)
                .show();

    }

    private void turnOnAndOffHD(String status){
        try {
            outJson.put("hd", status);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    private void init() throws JSONException {
        // To get display width and height
        DisplayMetrics dm = getApplicationContext().getResources().getDisplayMetrics();
        ConstantsUtil.displayWidth = dm.widthPixels;
        ConstantsUtil.displayHeight = dm.heightPixels;

        outJson = new JSONObject();
        outJson.put("hd", "off");
        outJson.put("width", ConstantsUtil.displayWidth);
        outJson.put("height", ConstantsUtil.displayHeight);
    }

    public static String readUTF8(DataInput in) throws IOException {
        int length = in.readInt();
        byte [] encoded = new byte[length];
        in.readFully(encoded);
        return new String(encoded, StandardCharsets.UTF_8);
    }

    public static void writeUTF8(String s, DataOutput out) throws IOException {
        byte [] encoded = s.getBytes(StandardCharsets.UTF_8);
        out.writeInt(encoded.length);
        out.write(encoded);
    }

    public static ArrayList<String> parseListToArray(String list){
        ArrayList<String> parsed = new ArrayList<>();
        String[] array = list.split("\"");

        for(int i = 1; i < array.length; i+=2){
            parsed.add(array[i]);
        }

        return parsed;
    }

    public void getFireImageFromServer(String value){
        String[] spltValue = value.split(":");
        spltValue[1] = spltValue[1].replaceFirst(" ", "");
        String[] fireInfo = spltValue[1].split("-");
        String date = fireInfo[1]+"-"+fireInfo[2] + "-" + fireInfo[3];
        DataTask fireDataTask = new DataTask(MainActivity.this, fireInfo[0], "fire", date);
        fireDataTask.execute();
    }

    private void showRecyclerView(String title, List<Item> items){
        if (recyclerPopupWindow == null) {
            recyclerPopupWindow = new RecyclerPopupWindow(items);
            int windowWidth = (int) (ConstantsUtil.displayWidth * (1 / 3.0));
            int windowHeight = (int) (ConstantsUtil.displayHeight * (3 / 5.0));
            recyclerPopupWindow.showPopupWindow(getApplicationContext(), bottomNavigationView, windowWidth, windowHeight, (int) (ConstantsUtil.displayWidth / 2) - (int) (windowWidth / 2), 0);
            recyclerPopupWindow.setTitle(title);
            recyclerPopupWindow.setCallBack(new RecyclerPopupWindow.CallBack() {
                @Override
                public void callback(String value) {
                    if (!"-1".equals(value)) {
                        getFireImageFromServer(value);
                    }
                    recyclerPopupWindow = null;
                }
            });
        }
    }

    private static class DataTask extends AsyncTask<Void, Void, Void> {
        private ProgressDialog dialog;
        private String cam;
        private String date;
        private Socket socket;
        private DataOutputStream out;
        private DataInputStream in;
        private JSONObject _outJson;
        private JSONObject _inJson;
        private List<Item> infoItems;
        private List<Item> logItems;
        private String dataType;
        private WeakReference<MainActivity> activityWeakReference;
        private Bitmap bitmap;

        DataTask(MainActivity activity, String camera, String dataType, String date) {
            activityWeakReference = new WeakReference<>(activity);
            if(!dataType.equals("fire")) {
                this.dialog = new ProgressDialog(activity);
            }
            this.cam = camera;
            this.dataType = dataType;
            this.date = date;
            if (dataType.equals("info"))
                infoItems = new ArrayList<>();
            else if (dataType.equals("log"))
                logItems = new ArrayList<>();
        }

        @Override
        protected void onPreExecute() {
            if(!dataType.equals("fire")) {
                dialog.setMessage("정보를 가져오는 중입니다. 잠시만 기다려주세요");
                dialog.show();
            }
        }


        protected Void doInBackground(Void... args) {
            try {
                socket = new Socket(ConstantsUtil.ip, ConstantsUtil.port);
                out = new DataOutputStream(socket.getOutputStream());
                in = new DataInputStream(socket.getInputStream());
                _outJson = new JSONObject();

                _outJson.put("status", this.dataType);
                _outJson.put("camera", cam);
                _outJson.put("date", date);
                _outJson.put("width", ConstantsUtil.displayWidth);
                _outJson.put("height", ConstantsUtil.displayHeight);
                writeUTF8(_outJson.toString(), out);

                _inJson = new JSONObject(readUTF8(in));
                if (this.dataType.equals("info")) {
                    infoItems.add(0, new Item("ID: " + cam, false));
                    infoItems.add(1, new Item("Installation date: " + _inJson.getString("install_date"), false));
                    infoItems.add(2, new Item("Location: " + _inJson.getString("location"), false));
                    infoItems.add(3, new Item("CALL: " + _inJson.getString("call"), false));
                } else if (this.dataType.equals("log")) {
                    int numOfLogs = _inJson.getInt("num_of_logs");
                    if (0 < numOfLogs) {
                        Log.d("JSON", _inJson.getString("date"));
                        ArrayList<String> parsedArray = parseListToArray(_inJson.getString("date"));

                        for (int i = 0; i < numOfLogs; i++) {
                            logItems.add(i, new Item(String.format(Locale.KOREA,"%03d", i + 1) + ": " + cam + "-" + parsedArray.get(i), false));
                        }
                    }
                }
                else if (this.dataType.equals("fire")) {
                    String mat_string = _inJson.getString("encoded");
                    byte[] raw_data = Base64.decode(mat_string, Base64.DEFAULT);
                    bitmap = BitmapFactory.decodeByteArray(raw_data, 0, raw_data.length);
                }
            } catch (JSONException | IOException e) {
                e.printStackTrace();
            }
            return null;
        }

        protected void onPostExecute(Void result) {
            // do UI work here
            if (!this.dataType.equals("fire")) {
                if (dialog.isShowing()) {
                    dialog.dismiss();
                    if (this.dataType.equals("info"))
                        activityWeakReference.get().showRecyclerView("CCTV Information", infoItems);
                    else if (this.dataType.equals("log"))
                        activityWeakReference.get().showRecyclerView("Fire log", logItems);
                }
            }else{
                activityWeakReference.get().ivPopup.setImageBitmap(bitmap);
                activityWeakReference.get().showFireImage(activityWeakReference.get().ivPopup, bitmap.getWidth(), bitmap.getHeight());
            }
        }
    }

    public static class NetworkTask extends AsyncTask<Void, Void, Void> {
        String addr;
        int port;
        Socket socket;
        DataOutputStream out;
        DataInputStream in;
        String mat_string;
        byte[] raw_data;
        private WeakReference<MainActivity> activityWeakReference;
        NetworkTask(MainActivity context, String addr, int port) throws JSONException {
            this.addr = addr;
            this.port = port;
            activityWeakReference = new WeakReference<>(context);
        }

        @Override
        protected void onPreExecute() {
            super.onPreExecute();
        }

        @Override
        protected Void doInBackground(Void... voids) {
            try{
                socket = new Socket(this.addr, this.port);
                //outStream = socket.getOutputStream();
                out = new DataOutputStream(socket.getOutputStream());
                in = new DataInputStream(socket.getInputStream());

                activityWeakReference.get().outJson.put("status", "conn");
                while(true) {
                    writeUTF8(activityWeakReference.get().outJson.toString(), out);
                    activityWeakReference.get().inJson = new JSONObject(readUTF8(in));
                    mat_string = activityWeakReference.get().inJson.getString("img");
                    raw_data = Base64.decode(mat_string, Base64.DEFAULT);

                    activityWeakReference.get().mBtm_receive = BitmapFactory.decodeByteArray(raw_data, 0, raw_data.length);
                    if(!activityWeakReference.get().isConnected)
                        break;
                    publishProgress();
                }
                activityWeakReference.get().outJson.put("status", "exit");
                writeUTF8( activityWeakReference.get().outJson.toString(), out);
                //outStream.write("Exit".getBytes("UTF-8"));
            }
            catch (Exception e){
                e.printStackTrace();
            }
            return null;
        }

        @Override
        protected void onProgressUpdate(Void... values) {
            super.onProgressUpdate(values);
            activityWeakReference.get().mIv_frame.setImageBitmap(activityWeakReference.get().mBtm_receive);
        }

        @Override
        protected void onPostExecute(Void aVoid)  {
            // TODO work after receiving data
            super.onPostExecute(aVoid);
            try {
                if (socket != null)
                    socket.close();
                activityWeakReference.get().mIv_mark.setVisibility(View.VISIBLE);
                activityWeakReference.get().mIv_frame.setVisibility(View.INVISIBLE);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

}