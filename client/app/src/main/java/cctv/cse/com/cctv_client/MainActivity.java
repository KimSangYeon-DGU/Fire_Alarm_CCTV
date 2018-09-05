package cctv.cse.com.cctv_client;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.AsyncTask;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.SocketAddress;

public class MainActivity extends AppCompatActivity {

    private Socket socket;
    public ImageView mIv_receive;
    public Bitmap mBtm_receive;
    ByteArrayOutputStream mBaos;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mIv_receive = (ImageView)findViewById(R.id.iv_receive);
        Button mBtn_receive = (Button) findViewById(R.id.btn_connect);

        // Set default image on receive ImageView
        mIv_receive.setImageDrawable(getResources().getDrawable(R.drawable.cannot_load_image));

        // When receive button is clicked
        mBtn_receive.setOnClickListener(new Button.OnClickListener(){
            @Override
            public void onClick(View v) {
                NetworkTask networkTask = new NetworkTask(
                        "your server ip",
                        9999
                );
                networkTask.execute();
            }
        });
    }

    public class NetworkTask extends AsyncTask<Void, Void, Void> {
        String addr;
        int port;
        SocketAddress socketAddress;
        String response;

        NetworkTask(String addr, int port) {
            this.addr = addr;
            this.port = port;
            //socketAddress = new InetSocketAddress(this.addr, this.port);
        }

        @Override
        protected Void doInBackground(Void... voids) {
            try{
                Socket socket = new Socket(this.addr, this.port);
                //socket.setSoTimeout(3000);
                //socket.connect(socketAddress, 3000);
                InputStream mIs = socket.getInputStream();

                mBaos = new ByteArrayOutputStream(4096);
                byte[] buffer = new byte[4096];
                int bytesRead;
                while((bytesRead = mIs.read(buffer)) != -1){
                    mBaos.write(buffer, 0, bytesRead);
                }
                socket.close();
                Log.d("Debug", "receive"+mBaos);
            }
            catch (Exception e){
                e.printStackTrace();
            }
            return null;
        }

        @Override
        protected void onPostExecute(Void aVoid) {
            // TODO work after receiving data
            if (mBaos != null) {
                byte[] bytes = mBaos.toByteArray();
                mBtm_receive = BitmapFactory.decodeByteArray(bytes, 0, bytes.length);
                mIv_receive.setImageBitmap(mBtm_receive);
            }
            super.onPostExecute(aVoid);
        }
    }
}
