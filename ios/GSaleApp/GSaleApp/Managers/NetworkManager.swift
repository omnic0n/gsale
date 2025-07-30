import Foundation
import UIKit

class NetworkManager {
    static let shared = NetworkManager()
    
    private let baseURL = "https://gsale.levimylesllc.com"
    private let session = URLSession.shared
    
    private init() {}
    
    // MARK: - Login
    func login(username: String, password: String) async throws -> LoginResponse {
        let url = URL(string: "\(baseURL)/login")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        
        // URL encode the parameters properly
        let usernameEncoded = username.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? username
        let passwordEncoded = password.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? password
        let body = "username=\(usernameEncoded)&password=\(passwordEncoded)"
        request.httpBody = body.data(using: .utf8)
        
        print("🌐 Making login request to: \(url)")
        print("📝 Request body: username=\(usernameEncoded)")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.serverError("Invalid response")
        }
        
        print("📡 Response status: \(httpResponse.statusCode)")
        
        // Check if we got a redirect (successful login)
        if httpResponse.statusCode == 302 || httpResponse.statusCode == 200 {
            // Extract session cookie from response headers
            var sessionCookie: String?
            if let allHeaders = httpResponse.allHeaderFields as? [String: String] {
                for (key, value) in allHeaders {
                    if key.lowercased() == "set-cookie" {
                        sessionCookie = value
                        break
                    }
                }
            }
            
            // Also check for cookies in the response body or headers
            if sessionCookie == nil {
                // Try to extract from Location header for 302 redirects
                if httpResponse.statusCode == 302 {
                    sessionCookie = "session=logged_in" // Simple session indicator
                }
            }
            
            // Login successful - create a response
            let loginResponse = LoginResponse(
                success: true,
                message: "Login successful",
                cookie: sessionCookie,
                user_id: nil,
                username: username,
                is_admin: false
            )
            
            print("🔐 Login successful - cookie: \(sessionCookie ?? "none")")
            return loginResponse
        }
        
        // If we get here, login failed
        let responseString = String(data: data, encoding: .utf8) ?? "Unknown error"
        print("❌ Login failed. Response: \(responseString)")
        
        throw NetworkError.unauthorized
    }
    
    // MARK: - Groups
    func getGroups() async throws -> [Group] {
        let url = URL(string: "\(baseURL)/groups/list")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        // Set up session cookies for authentication
        if let cookie = UserManager.shared.cookie {
            request.setValue(cookie, forHTTPHeaderField: "Cookie")
        }
        
        print("🌐 Making groups list request to: \(url)")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.serverError("Invalid response")
        }
        
        print("📡 Groups list response status: \(httpResponse.statusCode)")
        
        if httpResponse.statusCode == 401 {
            throw NetworkError.unauthorized
        }
        
        guard httpResponse.statusCode == 200 else {
            let responseString = String(data: data, encoding: .utf8) ?? "Unknown error"
            print("❌ Groups list request failed. Response: \(responseString)")
            throw NetworkError.serverError("HTTP \(httpResponse.statusCode)")
        }
        
        // Since the backend returns HTML, we'll parse it to extract group data
        let responseString = String(data: data, encoding: .utf8) ?? ""
        print("📄 Response body: \(responseString)")
        
        // For now, return empty array since parsing HTML is complex
        // TODO: Implement HTML parsing or create JSON API endpoints
        print("✅ Returning 0 groups (HTML parsing not implemented)")
        return []
    }
    
    func getGroupDetails(groupId: Int) async throws -> GroupDetail {
        let url = URL(string: "\(baseURL)/groups/describe?group_id=\(groupId)")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        // Set up session cookies for authentication
        if let cookie = UserManager.shared.cookie {
            request.setValue(cookie, forHTTPHeaderField: "Cookie")
        }
        
        print("🌐 Making group details request to: \(url)")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.serverError("Invalid response")
        }
        
        print("📡 Group details response status: \(httpResponse.statusCode)")
        
        if httpResponse.statusCode == 401 {
            throw NetworkError.unauthorized
        }
        
        guard httpResponse.statusCode == 200 else {
            let responseString = String(data: data, encoding: .utf8) ?? "Unknown error"
            print("❌ Group details request failed. Response: \(responseString)")
            throw NetworkError.serverError("HTTP \(httpResponse.statusCode)")
        }
        
        // For now, return empty group detail since parsing HTML is complex
        // TODO: Implement HTML parsing or create JSON API endpoints
        print("✅ Returning empty group details (HTML parsing not implemented)")
        throw NetworkError.serverError("Group details not implemented yet")
    }
    
    func addGroup(name: String, price: Double, date: Date, image: UIImage? = nil) async throws -> AddGroupResponse {
        let url = URL(string: "\(baseURL)/groups/create")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        
        // Set up session cookies for authentication
        if let cookie = UserManager.shared.cookie {
            request.setValue(cookie, forHTTPHeaderField: "Cookie")
            print("🍪 Using stored cookie: \(cookie)")
        } else {
            print("⚠️ No cookie found - user not logged in")
        }
        
        // Create form data for the groups/create endpoint
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd"
        let dateString = dateFormatter.string(from: date)
        
        // URL encode the parameters
        let dateEncoded = dateString.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? dateString
        let nameEncoded = name.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? name
        let priceEncoded = String(format: "%.2f", price).addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? String(format: "%.2f", price)
        
        // For now, use simple form data without image to test
        // TODO: Implement proper multipart form data for image upload
        let body = "date=\(dateEncoded)&name=\(nameEncoded)&price=\(priceEncoded)"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        request.httpBody = body.data(using: .utf8)
        
        print("🌐 Making add group request to: \(url)")
        print("📝 Request data: name=\(name), price=\(price), date=\(dateString)")
        print("📷 Image included: \(image != nil)")
        print("📋 Request headers: \(request.allHTTPHeaderFields ?? [:])")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.serverError("Invalid response")
        }
        
        print("📡 Add group response status: \(httpResponse.statusCode)")
        
        if httpResponse.statusCode == 401 {
            throw NetworkError.unauthorized
        }
        
        // Check for redirect to login (not authenticated)
        if httpResponse.statusCode == 302 {
            let locationHeader = httpResponse.allHeaderFields["Location"] as? String ?? ""
            if locationHeader.contains("/login") {
                print("❌ Not authenticated - redirecting to login")
                throw NetworkError.unauthorized
            }
            
            print("✅ Group created successfully (redirect)")
            return AddGroupResponse(
                success: true,
                message: "Group created successfully",
                group_id: nil
            )
        }
        
        // Check for 200 response but with potential error in body
        if httpResponse.statusCode == 200 {
            let responseString = String(data: data, encoding: .utf8) ?? ""
            print("📄 Response body: \(responseString)")
            
            // Check if response contains error indicators
            if responseString.contains("error") || responseString.contains("Error") || responseString.contains("failed") {
                print("❌ 200 response but contains error")
                throw NetworkError.serverError("Server returned error: \(responseString)")
            }
            
            // If we get here, it's a successful 200 response
            print("✅ Group created successfully (200)")
            return AddGroupResponse(
                success: true,
                message: "Group created successfully",
                group_id: nil
            )
        }
        
        // If we get here, something went wrong
        let responseString = String(data: data, encoding: .utf8) ?? "Unknown error"
        print("❌ Add group failed. Response: \(responseString)")
        print("📡 Response headers: \(httpResponse.allHeaderFields)")
        
        if httpResponse.statusCode == 500 {
            throw NetworkError.serverError("Server error (500) - \(responseString)")
        } else if httpResponse.statusCode == 400 {
            throw NetworkError.serverError("Bad request (400) - \(responseString)")
        } else {
            throw NetworkError.serverError("HTTP \(httpResponse.statusCode) - \(responseString)")
        }
    }
} 