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
import android.util.Log;
import android.view.MenuItem;
import android.view.View;
import android.widget.CompoundButton;
import android.widget.ImageView;
import android.widget.PopupWindow;

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

    public ImageView mIv_frame;
    public ImageView mIv_mark;
    public Bitmap mBtm_receive;
    NetworkTask networkTask;
    boolean isConnected;
    private BottomNavigationView bottomNavigationView;
    PopupWindow mPopupWindow;


    List<Item> items;
    private RecyclerPopupWindow recyclerPopupWindow;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main_land);
        init();
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
        bottomNavigationView.setOnNavigationItemReselectedListener(new BottomNavigationView.OnNavigationItemReselectedListener() {
            @Override
            public void onNavigationItemReselected(@NonNull MenuItem item) {
                switch (item.getItemId()) {
                    case R.id.bot_menu_home:
                        Log.d("DEBUG", "Home Reselected");
                        break;
                    case R.id.bot_menu_hd:
                        Log.d("DEBUG", "HD Reselected");
                        break;
                    case R.id.bot_menu_list:
                        Log.d("DEBUG", "List Reselected");
                        break;
                    case R.id.bot_menu_info:
                        Log.d("DEBUG", "Info Reselected");
                        break;
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
                        break;

                    case R.id.bot_menu_info:
                        Log.d("DEBUG", "Info Selected");
                        if (recyclerPopupWindow == null) {
                            recyclerPopupWindow = new RecyclerPopupWindow(items);
                            recyclerPopupWindow.showPopupWindow(MainActivity.this, bottomNavigationView, 700, 700);
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
                        /*
                        View popupView = getLayoutInflater().inflate(R.layout.dialog_activity, null);
                        mPopupWindow = new PopupWindow(popupView, LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
                        //popupView 에서 (LinearLayout 을 사용) 레이아웃이 둘러싸고 있는 컨텐츠의 크기 만큼 팝업 크기를 지정
                        mPopupWindow.setFocusable(true);
                        mPopupWindow.showAtLocation(popupView, Gravity.CENTER, 0, 0);

                        ImageView ivClose = (ImageView) popupView.findViewById(R.id.iv_close);

                        ivClose.setOnClickListener(new View.OnClickListener() {
                            @Override
                            public void onClick(View v) {
                                mPopupWindow.dismiss();
                            }
                        });

                        */
                        break;
                }
                return true;
            }
        });

    }

    private void init() {
        items = new ArrayList<>();
        items.add(0, new Item("取消", false));
        for (int i = 0; i < 60; ++i) {
            items.add(i + 1, new Item(i + "min", false));
        }
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