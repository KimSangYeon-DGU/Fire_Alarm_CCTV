package cctv.cse.com.cctv_client.activity;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;

import cctv.cse.com.cctv_client.R;
import cctv.cse.com.cctv_client.activity.MainActivity;

/**
 * Created by sy081 on 2018-09-14.
 * This is splash activity to show the main logo when app starts.
 */
public class SplashActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_splash);
        Thread myThread = new Thread(){
            @Override
            public void run() {
                try {
                    // Stop 3 seconds
                    sleep(3000);
                    // Get Main activity intent
                    Intent intent = new Intent(getApplicationContext(), MainActivity.class);

                    // Finish this activity
                    finish();

                    // Start main activity
                    startActivity(intent);

                    // Fade in and out animation
                    overridePendingTransition(R.anim.fade_in, R.anim.fade_out);

                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        };
        myThread.start();

    }
}
