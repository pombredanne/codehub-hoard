package com.bah.heimdall.util;

import java.util.ArrayList;
import java.util.List;
import com.bah.heimdall.common.AppConstants;
import org.apache.http.Header;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.conn.ssl.DefaultHostnameVerifier;
import org.apache.http.conn.ssl.SSLConnectionSocketFactory;
import org.apache.http.impl.client.BasicResponseHandler;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.ssl.SSLContextBuilder;
import org.apache.http.ssl.TrustStrategy;

public class IngestUtil {
    public static List<String> getHttpResponseWithHeaders(String url, Boolean continueOnErr){
        ArrayList<String> response = new ArrayList<String>();
        if(url.isEmpty())
            return response;

        try {
            //FIXME
            /** Please note: SSL certificate validation is disabled for now ***/
            SSLContextBuilder contextBuilder = SSLContextBuilder.create();
            contextBuilder.loadTrustMaterial(new TrustStrategy(){
                public boolean isTrusted(java.security.cert.X509Certificate[] var1, String var2) throws java.security.cert.CertificateException{
                    return true;
                }
            });

            SSLConnectionSocketFactory sslFactory = new SSLConnectionSocketFactory(contextBuilder.build(), new DefaultHostnameVerifier());
            HttpClientBuilder builder = HttpClients.custom().setSSLSocketFactory(sslFactory);
            HttpClient client = builder.build();
            HttpGet request = new HttpGet(url);
            HttpResponse httpResponse = client.execute(request);
            String responseString = new BasicResponseHandler().handleResponse(httpResponse);
            if(responseString == null){
                response.add("{\"" + AppConstants.STAGE_ERROR() + "\":\"Response body is empty\"}");
            }else {
                response.add(responseString);
            }

            for(Header header : httpResponse.getAllHeaders()){
                if("Link".equals(header.getName())){
                    response.add(header.getValue());
                    break;
                }
            }
        } catch (Exception e) {
            System.out.println(AppConstants.STAGE_ERROR() + "Error occurred while accessing : " + url);
            e.printStackTrace();
            response.add("{\""+AppConstants.STAGE_ERROR()+"\":\""+e.getMessage()+"\"}");
            if(! continueOnErr){
                throw new RuntimeException(e);
            }
        }
        return response;
    }
}