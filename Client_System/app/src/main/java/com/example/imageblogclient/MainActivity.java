package com.example.imageblogclient;

import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class MainActivity extends AppCompatActivity {

    private RecyclerView recyclerView;
    private ImageAdapter adapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        recyclerView = findViewById(R.id.recyclerView);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));

        fetchImages();
    }

    private void fetchImages() {
        ApiService apiService = ApiClient.getRetrofit().create(ApiService.class);
        Call<List<ImagePost>> call = apiService.getImages();

        call.enqueue(new Callback<List<ImagePost>>() {
            @Override
            public void onResponse(Call<List<ImagePost>> call, Response<List<ImagePost>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    adapter = new ImageAdapter(MainActivity.this, response.body());
                    recyclerView.setAdapter(adapter);
                }
            }

            @Override
            public void onFailure(Call<List<ImagePost>> call, Throwable t) {
                t.printStackTrace();
            }
        });
    }
}
