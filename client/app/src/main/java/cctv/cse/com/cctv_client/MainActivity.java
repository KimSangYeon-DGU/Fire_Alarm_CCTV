package cctv.cse.com.cctv_client;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.AsyncTask;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Base64;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;

import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.DataInput;
import java.io.DataInputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.net.Socket;
import java.net.SocketAddress;
import java.nio.charset.StandardCharsets;

public class MainActivity extends AppCompatActivity {

    public ImageView mIv_receive;
    public Bitmap mBtm_receive;
    NetworkTask networkTask;
    boolean isConnected;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        mIv_receive = (ImageView)findViewById(R.id.iv_receive);
        Button mBtn_receive = (Button) findViewById(R.id.btn_connect);


        // Set default image on receive ImageView
        mIv_receive.setImageDrawable(getResources().getDrawable(R.drawable.cannot_load_image));
        isConnected  = false;
        // initialize the worker

        // When receive button is clicked
        mBtn_receive.setOnClickListener(new Button.OnClickListener(){
            @Override
            public void onClick(View v) {
                if (isConnected == false) {
                    isConnected = true;
                    try {
                        networkTask = new NetworkTask(
                                "192.168.219.195",
                                8888
                        );

                        networkTask.execute();
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }else{
                    isConnected = false;
                    networkTask = null;
                }
            }
        });
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
            mIv_receive.setImageBitmap(mBtm_receive);
        }

        @Override
        protected void onPostExecute(Void aVoid)  {
            // TODO work after receiving data
            super.onPostExecute(aVoid);
            try {
                if (socket != null)
                    socket.close();
                mIv_receive.setImageDrawable(getResources().getDrawable(R.drawable.cannot_load_image));

            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

}