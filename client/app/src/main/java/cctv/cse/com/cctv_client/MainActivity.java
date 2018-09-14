package cctv.cse.com.cctv_client;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.os.AsyncTask;
import android.support.annotation.NonNull;
import android.support.design.widget.BottomNavigationView;
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
import android.widget.PopupWindow;
import android.widget.TextView;

import org.json.JSONObject;

import java.io.DataInput;
import java.io.DataInputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity {

    ImageView mIv_frame;
    ImageView mIv_mark;
    Bitmap mBtm_receive;
    NetworkTask networkTask;
    boolean isConnected;
    BottomNavigationView bottomNavigationView;
    List<Item> infoItems;
    List<Item> logItems;
    private RecyclerPopupWindow recyclerPopupWindow;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main_land);
        init();
        DisplayMetrics dm = getApplicationContext().getResources().getDisplayMetrics();

        Constants.displayWidth = dm.widthPixels;
        Constants.displayHeight = dm.heightPixels;

        mIv_frame = findViewById(R.id.iv_frame);
        mIv_mark = findViewById(R.id.iv_mark);
        bottomNavigationView = findViewById(R.id.bnv_menu);

        SwitchCompat switchCompat = findViewById(R.id.sc_connect);
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
                                    "10.70.22.222",
                                    8888
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
                        Log.d("DEBUG", "Home Selected");
                        break;

                    case R.id.bot_menu_hd:
                        Log.d("DEBUG", "HD Selected");
                        break;

                    case R.id.bot_menu_list:
                        Log.d("DEBUG", "List Selected");
                        if (recyclerPopupWindow == null) {
                            recyclerPopupWindow = new RecyclerPopupWindow(logItems);
                            int windowWidth =(int)(Constants.displayWidth*(1/3.0));
                            int windowHeight = (int)(Constants.displayHeight*(3/5.0));
                            recyclerPopupWindow.showPopupWindow(MainActivity.this, bottomNavigationView, windowWidth, windowHeight, (int)(Constants.displayWidth/2)-(int)(windowWidth/2), 0);
                            recyclerPopupWindow.setTitle("Fire Log");
                            recyclerPopupWindow.setCallBack(new RecyclerPopupWindow.CallBack() {
                                @Override
                                public void callback(String value) {
                                    if (!"-1".equals(value)) {
                                        //showUpBtn.setText(value);
                                    }
                                    recyclerPopupWindow = null;
                                }
                            });
                        }
                        break;

                    case R.id.bot_menu_info:
                        Log.d("DEBUG", "Info Selected");
                        if (recyclerPopupWindow == null) {
                            recyclerPopupWindow = new RecyclerPopupWindow(infoItems);
                            int windowWidth =(int)(Constants.displayWidth*(1/3.0));
                            int windowHeight = (int)(Constants.displayHeight*(3/5.0));
                            recyclerPopupWindow.showPopupWindow(MainActivity.this, bottomNavigationView, windowWidth, windowHeight, (int)(Constants.displayWidth/2)-(int)(windowWidth/2), 0);
                            recyclerPopupWindow.setTitle("CCTV Information");
                            recyclerPopupWindow.setCallBack(new RecyclerPopupWindow.CallBack() {
                                @Override
                                public void callback(String value) {
                                    if (!"-1".equals(value)) {
                                        //showUpBtn.setText(value);
                                    }
                                    recyclerPopupWindow = null;
                                }
                            });
                        }
                        break;

                    case R.id.bot_menu_call:
                        break;
                }
                return true;
            }
        });

    }

    private void init() {
        infoItems = new ArrayList<>();
        infoItems.add(0, new Item("ID: CAM01", false));
        infoItems.add(1, new Item("Installation date: 09-15-2018", false));
        infoItems.add(2, new Item("Location: Kitchen", false));
        infoItems.add(3, new Item("CALL: +82 10-xxxx-xxxx", false));

        logItems = new ArrayList<>();
        logItems.add(0, new Item("01: CAM01-XX-AA-20xx", false));
        logItems.add(1, new Item("02: CAM01-XX-AA-20xx", false));
        logItems.add(2, new Item("03: CAM01-XX-AA-20xx", false));
        logItems.add(3, new Item("04: CAM01-XX-AA-20xx", false));
        logItems.add(4, new Item("05: CAM01-XX-AA-20xx", false));
    }

    public String readUTF8(DataInput in) throws IOException {
        int length = in.readInt();
        byte [] encoded = new byte[length];
        in.readFully(encoded);
        return new String(encoded, StandardCharsets.UTF_8);
    }

    public class NetworkTask extends AsyncTask<Void, Void, Void> {
        String addr;
        int port;
        Socket socket;
        OutputStream outStream;
        DataInputStream in;
        JSONObject json;
        String mat_string;
        byte[] raw_data;

        NetworkTask(String addr, int port) {
            this.addr = addr;
            this.port = port;
        }

        @Override
        protected void onPreExecute() {
            super.onPreExecute();
            try {

            }
            catch (Exception e){
                e.printStackTrace();
            }
        }

        @Override
        protected Void doInBackground(Void... voids) {
            try{
                socket = new Socket(this.addr, this.port);
                outStream = socket.getOutputStream();
                in = new DataInputStream(socket.getInputStream());
                while(true) {
                    outStream.write("Conn".getBytes("UTF-8"));
                    json = new JSONObject(readUTF8(in));
                    //String leaf_name = json.getString("leaf");
                    mat_string = json.getString("img");
                    raw_data = Base64.decode(mat_string, Base64.DEFAULT);
                    mBtm_receive = BitmapFactory.decodeByteArray(raw_data, 0, raw_data.length);
                    if(isConnected == false)
                        break;
                    publishProgress();
                }
                outStream.write("Exit".getBytes("UTF-8"));
            }
            catch (Exception e){
                e.printStackTrace();
            }
            return null;
        }

        @Override
        protected void onProgressUpdate(Void... values) {
            super.onProgressUpdate(values);
            mIv_frame.setImageBitmap(mBtm_receive);
        }

        @Override
        protected void onPostExecute(Void aVoid)  {
            // TODO work after receiving data
            super.onPostExecute(aVoid);
            try {
                if (socket != null)
                    socket.close();
                //mIv_mark.setImageDrawable(getResources().getDrawable(R.drawable.stop));
                mIv_mark.setVisibility(View.VISIBLE);
                mIv_frame.setVisibility(View.INVISIBLE);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

}