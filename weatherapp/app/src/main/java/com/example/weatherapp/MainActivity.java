package com.example.weatherapp;


import android.os.AsyncTask;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.net.UnknownHostException;

public class MainActivity extends AppCompatActivity {

    TextView recieveText;
    EditText editTextAddress, editTextPort, message1Text,message2Text;
    Button connectBtn, clearBtn;

    Socket socket = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        //앱 기본 스타일 설정
        getSupportActionBar().setElevation(0);

        connectBtn = (Button) findViewById(R.id.buttonConnect);
        clearBtn = (Button) findViewById(R.id.buttonClear);
        recieveText = (TextView) findViewById(R.id.textViewReciev);
        message1Text = (EditText) findViewById(R.id.messageText2);
        message2Text = (EditText) findViewById(R.id.messageText1);
        //connect 버튼 클릭
        connectBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                MyClientTask myClientTask = new MyClientTask("10.0.2.2", 12000, message1Text.getText().toString(),message2Text.getText().toString());

                myClientTask.execute();
                //messageText.setText("");
            }
        });

        //clear 버튼 클릭
        clearBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                message1Text.setText("");
                message2Text.setText("");

            }
        });
    }

    //
    public class MyClientTask extends AsyncTask<Void, Void, Void> {
        String dstAddress;
        int dstPort;
        String response = "";
        String myMessage1 = "";
        String myMessage2 = "";

        //constructor
        MyClientTask(String addr, int port, String message1,String message2){
            dstAddress = addr;//이게 호스트
            dstPort = port;//이게 포트
            myMessage1 = message1;//날짜 선택
            myMessage2 = message2;//시간 선택
        }

        @Override
        protected Void doInBackground(Void... arg0) {

            Socket socket = null;
            myMessage1 = myMessage1.toString();
            myMessage2 = myMessage2.toString();
            try {
                socket = new Socket(dstAddress, dstPort);
                //송신
                OutputStream out = socket.getOutputStream();
                out.write(myMessage1.getBytes());
                out.write(myMessage2.getBytes());
                //수신
                ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream(1024);
                byte[] buffer = new byte[1024];
                String line="";

                int bytesRead;
                InputStream inputStream = socket.getInputStream();
                //BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream(),"UTF-8"))
                /*
                 * notice:
                 * inputStream.read() will block if no data return
                 */

                while ((bytesRead = inputStream.read(buffer)) != -1){
                    byteArrayOutputStream.write(buffer, 0, bytesRead);
                    response += byteArrayOutputStream.toString("UTF-8");
                }


                response = "추천 관광지 : " + response;

            } catch (UnknownHostException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
                response = "UnknownHostException: " + e.toString();
            } catch (IOException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
                response = "IOException: " + e.toString();
            }finally{
                if(socket != null){
                    try {
                        socket.close();
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                }
            }
            return null;
        }

        @Override
        protected void onPostExecute(Void result) {
            recieveText.setText(response);
            super.onPostExecute(result);
        }
    }
}