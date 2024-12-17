package com.example.imageblogclient;

import java.util.List;

import retrofit2.Call;
import retrofit2.http.GET;

public interface ApiService {
    @GET("api_root/ImagePost/")  // Replace with your Django endpoint
    Call<List<ImagePost>> getImages();
}

