package com.example.service;

import javax.ws.rs.*;
import javax.ws.rs.core.Response;
import java.sql.*;

/**
 * Example REST service for SAP ME/MII integration
 */
@Path("/api/v1")
public class TestService {
    
    @GET
    @Path("/orders")
    @Produces("application/json")
    public Response getOrders() {
        try {
            // Database connection example
            Connection conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/sap_me_db");
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery("SELECT * FROM orders WHERE status = 'ACTIVE'");
            
            // Process results
            while (rs.next()) {
                System.out.println(rs.getString("order_id"));
            }
            
            return Response.ok().build();
        } catch (SQLException e) {
            return Response.serverError().build();
        }
    }
    
    @POST
    @Path("/orders")
    @Consumes("application/json")
    public Response createOrder(String orderData) {
        try {
            // External API call example
            String apiUrl = "http://external-erp.example.com/api/orders/create";
            // HTTP client code here...
            
            // Database insert
            Connection conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/sap_me_db");
            PreparedStatement pstmt = conn.prepareStatement("INSERT INTO orders (data) VALUES (?)");
            pstmt.setString(1, orderData);
            pstmt.executeUpdate();
            
            return Response.status(201).build();
        } catch (Exception e) {
            return Response.serverError().build();
        }
    }
    
    @PUT
    @Path("/orders/{id}")
    public Response updateOrder(@PathParam("id") String orderId, String orderData) {
        // Update logic with SQL
        String sql = "UPDATE orders SET data = ? WHERE order_id = ?";
        return Response.ok().build();
    }
    
    @DELETE
    @Path("/orders/{id}")
    public Response deleteOrder(@PathParam("id") String orderId) {
        // Delete logic
        String sql = "DELETE FROM orders WHERE order_id = ?";
        return Response.noContent().build();
    }
    
    @GET
    @Path("/products")
    public Response getProducts() {
        // Another external call
        String url = "https://product-service.example.com/api/products";
        return Response.ok().build();
    }
}
