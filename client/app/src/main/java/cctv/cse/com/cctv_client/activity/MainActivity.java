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

/**
 * Created by sy081 on 2018-09-01.
 * Main activity.
 * Connect server and get data from it
 */
public class MainActivity extends AppCompatActivity {

    private ImageView ivFrame; // image view to show frame got from server
    private ImageView ivMark; // Center mark image view
    private Bitmap btmReceive; // frame received from server
    private NetworkTask networkTask; // For network with server
    private BottomNavigationView bottomNavigationView; // Bottom navigation view
    private RecyclerPopupWindow recyclerPopupWindow; // custom RecyclerPopupView
    private JSONObject inJson; // JSON data got from server
    private JSONObject outJson; // JSON data to send to server
    private boolean isConnected; // Check connection with server
    private ImageView ivPopup; // Image view for pop up to show previous fire image got from server
    private SwitchCompat switchCompat; // Switch to connect to server

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main_land);


        // For getting push notification's registration id
        String refreshedToken = FirebaseInstanceId.getInstance().getToken();
        Log.d("REGID",refreshedToken);

        // Initialized needed setting.
        try {
            init();
        } catch (JSONException e) {
            e.printStackTrace();
        }

        /* *
         * If switch is pushed, create asynchronous task for networking with server
         * If isConnected is false, connect to server.
         */
        switchCompat.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if (isChecked){
                    if (!isConnected) {
                        isConnected = true;
                        try {
                            // To show frame got from server, make mark image invisible.
                            // Likewise, make frame image view visible.
                            ivMark.setVisibility(View.INVISIBLE);
                            ivFrame.setVisibility(View.VISIBLE);

                            // Initialize the worker
                            networkTask = new NetworkTask(
                                    MainActivity.this,
                                    ConstantsUtil.ip,
                                    ConstantsUtil.port
                            );

                            // Execute the worker
                            networkTask.execute();

                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    }
                }
                // If switch is canceled, stop connecting.
                else{
                    isConnected = false;
                    networkTask = null;
                }
            }
        });

        /* *
         * Set bottom navigation view selected listener
         * home: default mode
         * hd: high resolution
         * log: previous fire date list
         * info: cctv information
         * call: call 119
         */
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

                    case R.id.bot_menu_log:
                        turnOnAndOffHD("off");
                        switchCompat.setChecked(false);
                        showConnectDialog("CAM01","log", "null");
                        break;

                    case R.id.bot_menu_info:
                        turnOnAndOffHD("off");
                        switchCompat.setChecked(false);
                        showConnectDialog("CAM01","info", "null");
                        break;

                    case R.id.bot_menu_call:
                        // Turn off TCT socket stream.
                        turnOnAndOffHD("off");
                        String phone = "119";
                        // Change current intent to call
                        Intent intent = new Intent(Intent.ACTION_DIAL, Uri.fromParts("tel", phone, null));
                        startActivity(intent);
                        break;
                }
                return true;
            }
        });

    }

    /* *
     * Initialized each component.
     */
    private void init() throws JSONException {
        // To get display width and height
        DisplayMetrics dm = getApplicationContext().getResources().getDisplayMetrics();
        ConstantsUtil.displayWidth = dm.widthPixels;
        ConstantsUtil.displayHeight = dm.heightPixels;

        isConnected  = false;

        // Initialize dummy image view for fire image
        ivPopup = new ImageView(this);

        // Initialize components according to id.
        ivFrame = findViewById(R.id.iv_frame);
        ivMark = findViewById(R.id.iv_mark);
        bottomNavigationView = findViewById(R.id.bnv_menu);
        switchCompat = findViewById(R.id.sc_connect);

        // Set default image of Mark ImageView
        ivMark.setImageDrawable(getResources().getDrawable(R.drawable.stop));
        ivFrame.setBackgroundColor(Color.WHITE);

        // Set ImageView visibility
        ivFrame.setVisibility(View.INVISIBLE);
        ivMark.setVisibility(View.VISIBLE);

        // Set default json structure to send
        outJson = new JSONObject();
        outJson.put("hd", "off");
        outJson.put("width", ConstantsUtil.displayWidth);
        outJson.put("height", ConstantsUtil.displayHeight);

    }

    /**
     * This is function to show fire image got from server
     */
    private void showFireImage(ImageView imageView, int width, int height) {
        final ImagePopup imagePopup = new ImagePopup(this);
        imagePopup.initiatePopup(imageView.getDrawable());
        imagePopup.setWindowWidth((int)(ConstantsUtil.displayWidth/1.5));
        imagePopup.setWindowHeight((int)(ConstantsUtil.displayHeight/1.5));
        imagePopup.viewPopup();
    }

    /**
     * This is function to show dialog to get permission to connect to server.
     */
    private void showConnectDialog(final String camera, final String dataType, final String date){
        final AlertDialog.Builder alertDialog = new AlertDialog.Builder(this, R.style.Theme_AppCompat_Light_Dialog_Alert);
        alertDialog.setMessage(R.string.conn_context)
                .setTitle(R.string.conn_name)
                .setPositiveButton("Yes", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        dialog.cancel();
                        DataTask infoDataTask = new DataTask(MainActivity.this, camera, dataType, date);
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

    /**
     * This is function to turn off HD mode.
     */
    private void turnOnAndOffHD(String status){
        try {
            outJson.put("hd", status);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    /**
     * This is made to communicate with python server.
     */
    public static String readUTF8(DataInput in) throws IOException {
        // Read the length of message
        int length = in.readInt();
        byte [] encoded = new byte[length];

        // Read message
        in.readFully(encoded);

        // Return encoded message in UTF-8 format.
        return new String(encoded, StandardCharsets.UTF_8);
    }

    /**
     * This is made to communicate with python server.
     */
    public static void writeUTF8(String msg, DataOutput out) throws IOException {
        // Convert bytes to string in UTF-8 foramt.
        byte [] encoded = msg.getBytes(StandardCharsets.UTF_8);

        // Write length of encoded message
        out.writeInt(encoded.length);

        // Write message
        out.write(encoded);
    }

    /**
     * This is made to extract required data in python dictionary, but java dose not provide dictionary data structure.
     * So, I have to implement replacement function.
     * I used the fact that the data that I needed data were classified by index.
     * The data I needed is date in fire log.
     */
    public static ArrayList<String> parseListToArray(String list){
        ArrayList<String> parsed = new ArrayList<>();
        String[] array = list.split("\"");

        for(int i = 1; i < array.length; i+=2){
            parsed.add(array[i]);
        }

        return parsed;
    }

    /**
     * This is made to get previous detected fire image from server
     * The string was parsed to match the format.
     */
    private void getFireImageFromServer(String value){
        // Parsing for figuring out the fire image name.
        String[] spltValue = value.split(":");
        spltValue[1] = spltValue[1].replaceFirst(" ", "");
        String[] fireInfo = spltValue[1].split("-");
        String date = fireInfo[1]+"-"+fireInfo[2] + "-" + fireInfo[3];

        // Create fire data task object for getting fire image from server
        DataTask fireDataTask = new DataTask(MainActivity.this, fireInfo[0], "fire", date);

        // Run AsyncTask
        fireDataTask.execute();
    }

    /**
     * This is made to show recycler view at a center of screen
     */
    private void showRecyclerView(String title, List<Item> items){
        if (recyclerPopupWindow == null) {
            recyclerPopupWindow = new RecyclerPopupWindow(items);
            int windowWidth = (int) (ConstantsUtil.displayWidth * (1 / 3.0));
            int windowHeight = (int) (ConstantsUtil.displayHeight * (3 / 5.0));
            recyclerPopupWindow.showPopupWindow(getApplicationContext(), bottomNavigationView, windowWidth, windowHeight, (int) (ConstantsUtil.displayWidth / 2) - (int) (windowWidth / 2), 0);

            // Set title of view
            recyclerPopupWindow.setTitle(title);

            // If item of log is clicked, the callback function is called.
            recyclerPopupWindow.setCallBack(new RecyclerPopupWindow.CallBack() {
                @Override
                public void callback(String value) {
                    if (!"-1".equals(value)) {
                        // Convert string to target image name and get image from server using getFireImageFromServer function.
                        getFireImageFromServer(value);
                    }
                    // close window.
                    recyclerPopupWindow = null;
                }
            });
        }
    }

    /**
     * This is inner class to process socket communication with server asynchronously.
     * There are 3 modes, log, fire, and info.
     */
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

        /**
         * This is constructor to set initial value.
         */
        DataTask(MainActivity activity, String camera, String dataType, String date) {

            // Initialized WeakReference to MainActivity to access its resource.
            activityWeakReference = new WeakReference<>(activity);

            // If the data type is fire, do not show progress dialog for preventing crashing resources.
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

        /**
         * This function is called before the thread starts.
         */
        @Override
        protected void onPreExecute() {
            if(!dataType.equals("fire")) {
                // Set dialog message
                dialog.setMessage("정보를 가져오는 중입니다. 잠시만 기다려주세요");
                dialog.show();
            }
        }

        /**
         * This function is called when the thread starts.
         */
        protected Void doInBackground(Void... args) {
            try {
                // Set required socket, json data.
                socket = new Socket(ConstantsUtil.ip, ConstantsUtil.port);
                out = new DataOutputStream(socket.getOutputStream());
                in = new DataInputStream(socket.getInputStream());

                // Set json format.
                _outJson = new JSONObject();
                _outJson.put("status", this.dataType);
                _outJson.put("camera", cam);
                _outJson.put("date", date);
                _outJson.put("width", ConstantsUtil.displayWidth);
                _outJson.put("height", ConstantsUtil.displayHeight);

                // Write json data to server
                writeUTF8(_outJson.toString(), out);


                // Read data from server
                _inJson = new JSONObject(readUTF8(in));

                /* *
                 * Process each mode.
                 * info: add info data to items list
                 * log: parsing string first, then add log data to log list
                 * fire: convert a string through a byte array to a bitmap.
                 */
                if (this.dataType.equals("info")) {
                    infoItems.add(0, new Item("ID: " + cam, false));
                    infoItems.add(1, new Item("Installation date: " + _inJson.getString("install_date"), false));
                    infoItems.add(2, new Item("Location: " + _inJson.getString("location"), false));
                    infoItems.add(3, new Item("CALL: " + _inJson.getString("call"), false));
                    infoItems.add(4, new Item("License: " + _inJson.getString("license"), false));
                } else if (this.dataType.equals("log")) {
                    int numOfLogs = _inJson.getInt("num_of_logs");
                    if (0 < numOfLogs) {
                        Log.d("JSON", _inJson.getString("date"));
                        ArrayList<String> parsedArray = parseListToArray(_inJson.getString("date"));

                        for (int i = numOfLogs-1; i >= 0; --i) {
                            logItems.add(numOfLogs-i-1, new Item(String.format(Locale.KOREA,"%03d", numOfLogs-i) + ": " + cam + "-" + parsedArray.get(i), false));
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

        /**
         * This function is called when the thread ends.
         * The last operation is usually carried out here.
         */
        protected void onPostExecute(Void result) {
            /* *
             * If data type is not fire, show recycler view according to data type.
             * If it is fire, show fire image using popup window view.
             */
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

    /**
     * This is inner class to process socket communication with server asynchronously.
     * It is used to get images from servers.
     */
    public static class NetworkTask extends AsyncTask<Void, Void, Void> {
        private String addr;
        private int port;
        private Socket socket;
        private DataOutputStream out;
        private DataInputStream in;
        private String mat_string;
        private byte[] raw_data;
        private WeakReference<MainActivity> activityWeakReference;

        /**
         * This is constructor to set initial value.
         */
        NetworkTask(MainActivity context, String addr, int port) throws JSONException {
            this.addr = addr;
            this.port = port;
            activityWeakReference = new WeakReference<>(context);
        }

        @Override
        protected void onPreExecute() {
            super.onPreExecute();
        }

        /**
         * This function is called when the thread starts.
         */
        @Override
        protected Void doInBackground(Void... voids) {
            try{
                // Create socket and input-output data streams.
                socket = new Socket(this.addr, this.port);
                //outStream = socket.getOutputStream();
                out = new DataOutputStream(socket.getOutputStream());
                in = new DataInputStream(socket.getInputStream());

                // Put "conn" into status key for connection.
                activityWeakReference.get().outJson.put("status", "conn");

                while(true) {
                    // Write outJson to get cctv image.
                    writeUTF8(activityWeakReference.get().outJson.toString(), out);

                    // Read cctv image
                    activityWeakReference.get().inJson = new JSONObject(readUTF8(in));

                    // Get matrix string from json data["img"]
                    mat_string = activityWeakReference.get().inJson.getString("img");

                    // Decode string to byte array
                    raw_data = Base64.decode(mat_string, Base64.DEFAULT);

                    // Convert byte array to bitmap
                    activityWeakReference.get().btmReceive = BitmapFactory.decodeByteArray(raw_data, 0, raw_data.length);

                    // If isConnected is false, stop next communication.
                    if(!activityWeakReference.get().isConnected)
                        break;

                    // It should be called to update UI.
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

        // Update UI with new bitmap image
        @Override
        protected void onProgressUpdate(Void... values) {
            super.onProgressUpdate(values);

            // update ivFrame with new image got from server.
            activityWeakReference.get().ivFrame.setImageBitmap(activityWeakReference.get().btmReceive);
        }


        // This is called when the thread ends, and the last operation is executed here.
        @Override
        protected void onPostExecute(Void aVoid)  {
            // TODO work after receiving data
            super.onPostExecute(aVoid);
            try {
                if (socket != null)
                    socket.close();
                activityWeakReference.get().ivMark.setVisibility(View.VISIBLE);
                activityWeakReference.get().ivFrame.setVisibility(View.INVISIBLE);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

}