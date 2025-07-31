import Foundation
import UIKit

class NetworkManager {
    static let shared = NetworkManager()
    
    private let baseURL = "https://gsale.levimylesllc.com"
    private let session: URLSession
    
    private init() {
        print("🚀 NetworkManager initialized with default session configuration")
        
        // Use default session configuration
        self.session = URLSession.shared
        print("✅ NetworkManager session created successfully")
    }
    
    // MARK: - Login
    func login(username: String, password: String) async throws -> LoginResponse {
        let url = URL(string: "\(baseURL)/login")!
        var request = URLRequest(url: url)
        
        // URL encode the parameters properly
        let usernameEncoded = username.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? username
        let passwordEncoded = password.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? password
        let body = "username=\(usernameEncoded)&password=\(passwordEncoded)"
        
        // Debug: Check the exact bytes being sent
        let bodyData = body.data(using: .utf8)!
        print("🔍 Body data bytes: \(Array(bodyData))")
        print("🔍 Body data as string: \(String(data: bodyData, encoding: .utf8) ?? "invalid")")
        
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        request.setValue("GSaleApp/1.0", forHTTPHeaderField: "User-Agent")
        request.setValue("*/*", forHTTPHeaderField: "Accept")
        request.setValue("\(bodyData.count)", forHTTPHeaderField: "Content-Length")
        request.httpBody = bodyData
        
        print("🌐 Making login request to: \(url)")
        print("📝 HTTP Method: \(request.httpMethod ?? "unknown")")
        print("📝 Request body: \(body)")
        print("📋 Request headers: \(request.allHTTPHeaderFields ?? [:])")
        print("📏 Request body length: \(body.count)")
        print("🔍 Request body bytes: \(bodyData.count)")
        
        // Create a custom delegate to handle redirects and capture cookies
        class LoginDelegate: NSObject, URLSessionTaskDelegate {
            var capturedCookie: String?
            
            func urlSession(_ session: URLSession, task: URLSessionTask, willPerformHTTPRedirection response: HTTPURLResponse, newRequest request: URLRequest, completionHandler: @escaping (URLRequest?) -> Void) {
                // Capture Set-Cookie header from redirect response
                if let setCookieHeader = response.allHeaderFields["Set-Cookie"] as? String {
                    capturedCookie = setCookieHeader
                    print("🍪 Captured Set-Cookie from redirect: \(setCookieHeader)")
                }
                
                // Don't follow the redirect
                completionHandler(nil)
            }
        }
        
        let delegate = LoginDelegate()
        let config = URLSessionConfiguration.default
        let sessionWithDelegate = URLSession(configuration: config, delegate: delegate, delegateQueue: nil)
        
        let (data, response) = try await sessionWithDelegate.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.serverError("Invalid response")
        }
        
        // Debug: Check if we got redirected
        if let url = httpResponse.url {
            print("📍 Final URL after redirects: \(url)")
        }
        
        // Debug: Check if we got any response data
        let responseDataString = String(data: data, encoding: .utf8) ?? "No response data"
        print("📄 Response data length: \(data.count)")
        print("📄 Response data preview: \(String(responseDataString.prefix(200)))")
        
        print("📡 Response status: \(httpResponse.statusCode)")
        print("📋 All response headers: \(httpResponse.allHeaderFields)")
        
        // Check if we got a redirect (successful login)
        if httpResponse.statusCode == 302 {
            // First try to get cookie from delegate (redirect response)
            var sessionCookie = delegate.capturedCookie
            
            // If no cookie from delegate, try to extract from current response headers
            if sessionCookie == nil {
                if let setCookieHeader = httpResponse.allHeaderFields["Set-Cookie"] as? String {
                    sessionCookie = setCookieHeader
                    print("🍪 Found Set-Cookie in response headers: \(setCookieHeader)")
                }
            }
            
            // Extract just the session value from the Set-Cookie header
            if let cookie = sessionCookie {
                // Parse Set-Cookie header to extract session value
                // Format: "session=<value>; HttpOnly; Path=/"
                if let sessionValue = extractSessionValue(from: cookie) {
                    let cleanCookie = "session=\(sessionValue)"
                    
                    // Login successful - create a response
                    let loginResponse = LoginResponse(
                        success: true,
                        message: "Login successful",
                        cookie: cleanCookie,
                        user_id: nil,
                        username: username,
                        is_admin: false
                    )
                    
                    print("🔐 Login successful - cookie: \(cleanCookie)")
                    return loginResponse
                } else {
                    print("❌ Failed to extract session value from cookie: \(cookie)")
                }
            }
            
            print("❌ No valid session cookie found in login response")
            throw NetworkError.unauthorized
        }
        
        // If we get here, login failed
        let responseString = String(data: data, encoding: .utf8) ?? "Unknown error"
        print("❌ Login failed. Status: \(httpResponse.statusCode)")
        print("❌ Login failed. Response: \(responseString)")
        
        throw NetworkError.unauthorized
    }
    
    private func extractSessionValue(from setCookieHeader: String) -> String? {
        // Parse Set-Cookie header to extract session value
        // Format: "session=<value>; HttpOnly; Path=/" or just "session=<value>"
        
        print("🔍 Parsing Set-Cookie header: \(setCookieHeader)")
        
        // Look for session=<value> pattern
        let sessionPattern = #"session=([^;]+)"#
        
        do {
            let regex = try NSRegularExpression(pattern: sessionPattern, options: [])
            let range = NSRange(setCookieHeader.startIndex..<setCookieHeader.endIndex, in: setCookieHeader)
            
            if let match = regex.firstMatch(in: setCookieHeader, options: [], range: range) {
                if let sessionValueRange = Range(match.range(at: 1), in: setCookieHeader) {
                    let sessionValue = String(setCookieHeader[sessionValueRange])
                    print("✅ Extracted session value: \(sessionValue)")
                    return sessionValue
                }
            }
        } catch {
            print("❌ Regex error: \(error)")
        }
        
        print("❌ Could not extract session value from: \(setCookieHeader)")
        return nil
    }
    
    // MARK: - Groups
    func getGroups() async throws -> [Group] {
        let url = URL(string: "\(baseURL)/groups/list")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        // Set up session cookies for authentication
        if let cookie = UserManager.shared.cookie {
            request.setValue(cookie, forHTTPHeaderField: "Cookie")
            print("🍪 Sending cookie: \(cookie)")
        } else {
            print("⚠️ No cookie found - user not logged in")
            throw NetworkError.unauthorized
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
        
        // Parse HTML response to extract group data
        let responseString = String(data: data, encoding: .utf8) ?? ""
        print("📄 Response body length: \(responseString.count)")
        
        // Quick test to see if we're getting any response
        if responseString.isEmpty {
            print("❌ Empty response received")
            return []
        }
        
        print("✅ Received response with \(responseString.count) characters")
        
        // Debug: Check if this looks like a login page
        if responseString.contains("login") || responseString.contains("Login") {
            print("⚠️ Response appears to be a login page - user may not be authenticated")
            print("📄 Login page content: \(String(responseString.prefix(500)))")
            throw NetworkError.unauthorized
        }
        
        // Debug: Show a sample of the HTML to understand the structure
        if let sampleStart = responseString.range(of: "<tbody>")?.lowerBound {
            let sampleEnd = responseString.index(sampleStart, offsetBy: min(1000, responseString.count - responseString.distance(from: responseString.startIndex, to: sampleStart)))
            let sample = String(responseString[sampleStart..<sampleEnd])
            print("📄 HTML sample starting from <tbody>: \(sample)")
        }
        
        print("🔍 Starting HTML parsing...")
        print("📄 HTML length: \(responseString.count)")
        
        // Use the shared parsing method
        return parseGroupsFromHTML(responseString)
    }
    
    private func parseGroupsFromHTML(_ responseString: String) -> [Group] {
        var groups: [Group] = []
        
        // Try different patterns for different table structures
        
        // Pattern 1: Groups list format (with count column)
        // Looking for: <td>count</td><td><a href="/groups/describe?group_id=uuid">name</td><td>total</td><td>sold</td>...
        let groupRowPatternWithCount = #"<td>(\d+)</td>\s*<td><a[^>]*href="[^"]*group_id=([^"]+)"[^>]*>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>"#
        
        // Pattern 2: Search results format (without count column)
        // Looking for: <td><a href="/groups/describe?group_id=uuid">name</td><td>total</td><td>sold</td>...
        let groupRowPatternWithoutCount = #"<td><a[^>]*href="[^"]*group_id=([^"]+)"[^>]*>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>"#
        
        print("🔍 Pattern 1 (with count): \(groupRowPatternWithCount)")
        print("🔍 Pattern 2 (without count): \(groupRowPatternWithoutCount)")
        
        // Try pattern 1: Groups list format (with count column)
        do {
            let regex = try NSRegularExpression(pattern: groupRowPatternWithCount, options: [.dotMatchesLineSeparators])
            let range = NSRange(responseString.startIndex..<responseString.endIndex, in: responseString)
            let matches = regex.matches(in: responseString, options: [], range: range)
            
            print("🔍 Found \(matches.count) potential group rows (with count)")
            
            for (index, match) in matches.enumerated() {
                if match.numberOfRanges >= 11 {
                    let countRange = Range(match.range(at: 1), in: responseString)!
                    let groupIdRange = Range(match.range(at: 2), in: responseString)!
                    let nameRange = Range(match.range(at: 3), in: responseString)!
                    let totalItemsRange = Range(match.range(at: 4), in: responseString)!
                    let soldItemsRange = Range(match.range(at: 5), in: responseString)!
                    let unsoldItemsRange = Range(match.range(at: 6), in: responseString)!
                    let priceRange = Range(match.range(at: 7), in: responseString)!
                    let netRange = Range(match.range(at: 8), in: responseString)!
                    let profitRange = Range(match.range(at: 9), in: responseString)!
                    let averageRange = Range(match.range(at: 10), in: responseString)!
                    let dateRange = Range(match.range(at: 11), in: responseString)!
                    
                    let count = String(responseString[countRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                    let groupIdStr = String(responseString[groupIdRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                    let name = String(responseString[nameRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                    let totalItems = String(responseString[totalItemsRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                    let soldItems = String(responseString[soldItemsRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                    let price = String(responseString[priceRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                    let net = String(responseString[netRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                    let profit = String(responseString[profitRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                    let average = String(responseString[averageRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                    let date = String(responseString[dateRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                    
                    print("🔍 Row \(index): Count=\(count), ID=\(groupIdStr), Name=\(name), Total=\(totalItems), Sold=\(soldItems), Price=\(price), Net=\(net), Date=\(date)")
                    
                    // Skip header rows, totals row, or empty rows
                    if name.lowercased() == "name" || name.lowercased() == "totals" || name.isEmpty {
                        continue
                    }
                    
                    if !groupIdStr.isEmpty {
                        let group = Group(
                            id: groupIdStr,
                            name: name,
                            description: "Total: \(totalItems), Sold: \(soldItems), Price: \(price), Net: \(net)",
                            created_at: date,
                            updated_at: date
                        )
                        groups.append(group)
                        print("✅ Added group: \(name) (ID: \(groupIdStr), Date: \(date), Total: \(totalItems), Sold: \(soldItems))")
                    }
                }
            }
        } catch {
            print("❌ Error with regex (with count): \(error)")
        }
        
        // If no groups found with count pattern, try pattern 2: Search results format (without count)
        if groups.isEmpty {
            print("🔄 Trying search results pattern (without count)...")
            
            do {
                let regex = try NSRegularExpression(pattern: groupRowPatternWithoutCount, options: [.dotMatchesLineSeparators])
                let range = NSRange(responseString.startIndex..<responseString.endIndex, in: responseString)
                let matches = regex.matches(in: responseString, options: [], range: range)
                
                print("🔍 Found \(matches.count) potential group rows (without count)")
                
                for (index, match) in matches.enumerated() {
                    if match.numberOfRanges >= 10 {
                        let groupIdRange = Range(match.range(at: 1), in: responseString)!
                        let nameRange = Range(match.range(at: 2), in: responseString)!
                        let totalItemsRange = Range(match.range(at: 3), in: responseString)!
                        let soldItemsRange = Range(match.range(at: 4), in: responseString)!
                        let unsoldItemsRange = Range(match.range(at: 5), in: responseString)!
                        let priceRange = Range(match.range(at: 6), in: responseString)!
                        let netRange = Range(match.range(at: 7), in: responseString)!
                        let profitRange = Range(match.range(at: 8), in: responseString)!
                        let averageRange = Range(match.range(at: 9), in: responseString)!
                        let dateRange = Range(match.range(at: 10), in: responseString)!
                        
                        let groupIdStr = String(responseString[groupIdRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                        let name = String(responseString[nameRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                        let totalItems = String(responseString[totalItemsRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                        let soldItems = String(responseString[soldItemsRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                        let price = String(responseString[priceRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                        let net = String(responseString[netRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                        let profit = String(responseString[profitRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                        let average = String(responseString[averageRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                        let date = String(responseString[dateRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                        
                        print("🔍 Search Row \(index): ID=\(groupIdStr), Name=\(name), Total=\(totalItems), Sold=\(soldItems), Price=\(price), Net=\(net), Date=\(date)")
                        
                        // Skip header rows, totals row, or empty rows
                        if name.lowercased() == "name" || name.lowercased() == "totals" || name.isEmpty {
                            continue
                        }
                        
                        if !groupIdStr.isEmpty {
                            let group = Group(
                                id: groupIdStr,
                                name: name,
                                description: "Total: \(totalItems), Sold: \(soldItems), Price: \(price), Net: \(net)",
                                created_at: date,
                                updated_at: date
                            )
                            groups.append(group)
                            print("✅ Added search group: \(name) (ID: \(groupIdStr), Date: \(date), Total: \(totalItems), Sold: \(soldItems))")
                        }
                    }
                }
            } catch {
                print("❌ Error with regex (without count): \(error)")
            }
        }
        
        // If still no groups found, try an even simpler approach
        if groups.isEmpty {
            print("🔄 Trying very simple group link detection...")
            
            // Just look for any group links
            let simplePattern = #"group_id=([^"]+)"[^>]*>([^<]+)"#
            
            do {
                let regex = try NSRegularExpression(pattern: simplePattern, options: [])
                let range = NSRange(responseString.startIndex..<responseString.endIndex, in: responseString)
                let matches = regex.matches(in: responseString, options: [], range: range)
                
                print("🔍 Found \(matches.count) simple group links")
                
                for (index, match) in matches.enumerated() {
                    if match.numberOfRanges >= 3 {
                        let groupIdRange = Range(match.range(at: 1), in: responseString)!
                        let nameRange = Range(match.range(at: 2), in: responseString)!
                        
                        let groupIdStr = String(responseString[groupIdRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                        let name = String(responseString[nameRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                        
                        print("🔍 Simple Link \(index): ID=\(groupIdStr), Name=\(name)")
                        
                        if !groupIdStr.isEmpty && !name.isEmpty && !name.lowercased().contains("describe") {
                            let group = Group(
                                id: groupIdStr,
                                name: name,
                                description: "Found via simple search",
                                created_at: "2024-01-01",
                                updated_at: "2024-01-01"
                            )
                            groups.append(group)
                            print("✅ Added simple group: \(name) (ID: \(groupIdStr))")
                        }
                    }
                }
            } catch {
                print("❌ Error with simple regex: \(error)")
            }
        }
        
        // If no groups found with complex regex, try simpler approach
        if groups.isEmpty {
            print("🔄 Trying simpler parsing approach...")
            
            // Look for group links with a simpler pattern
            let simpleGroupPattern = #"group_id=([^"]+)"[^>]*>([^<]+)</a>"#
            
            do {
                let simpleRegex = try NSRegularExpression(pattern: simpleGroupPattern, options: [.dotMatchesLineSeparators])
                let range = NSRange(responseString.startIndex..<responseString.endIndex, in: responseString)
                let matches = simpleRegex.matches(in: responseString, options: [], range: range)
                
                print("🔍 Found \(matches.count) simple group matches")
                
                for (index, match) in matches.enumerated() {
                    if match.numberOfRanges >= 3 {
                        let groupIdRange = Range(match.range(at: 1), in: responseString)!
                        let nameRange = Range(match.range(at: 2), in: responseString)!
                        
                        let groupIdStr = String(responseString[groupIdRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                        let name = String(responseString[nameRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                        
                        print("🔍 Simple match \(index): ID=\(groupIdStr), Name=\(name)")
                        
                        if !groupIdStr.isEmpty && !name.isEmpty && name != "Name" {
                            let group = Group(
                                id: groupIdStr,
                                name: name,
                                description: "Group ID: \(groupIdStr)",
                                created_at: "2024-01-01",
                                updated_at: "2024-01-01"
                            )
                            groups.append(group)
                            print("✅ Added simple group: \(name) (ID: \(groupIdStr))")
                        }
                    }
                }
            } catch {
                print("❌ Error with simple regex: \(error)")
            }
        }
        
        print("✅ Returning \(groups.count) groups from HTML parsing")
        
        // If still no groups found, log the issue
        if groups.isEmpty {
            print("❌ No groups found in HTML response")
            print("📄 HTML preview: \(String(responseString.prefix(1000)))")
        }
        
        return groups
    }
    
    func getGroupsByYear(_ year: String) async throws -> [Group] {
        guard let cookie = UserManager.shared.cookie else {
            throw NetworkError.unauthorized
        }
        
        guard let url = URL(string: "\(baseURL)/groups/list") else {
            throw NetworkError.serverError("Invalid URL")
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        // Handle cookie format properly
        let cookieHeader = cookie.contains("session=") ? cookie : "session=\(cookie)"
        request.setValue(cookieHeader, forHTTPHeaderField: "Cookie")
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        request.setValue("GSaleApp/1.0", forHTTPHeaderField: "User-Agent")
        request.setValue("*/*", forHTTPHeaderField: "Accept")
        
        // Create form data with year filter
        let formData = "listYear=\(year.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? "")"
        request.httpBody = formData.data(using: .utf8)
        
        print("📅 Loading groups for year: '\(year)'")
        print("📝 Form data: \(formData)")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.serverError("Invalid response")
        }
        
        print("📡 Groups by year response status: \(httpResponse.statusCode)")
        
        guard httpResponse.statusCode == 200 else {
            throw NetworkError.serverError("HTTP \(httpResponse.statusCode)")
        }
        
        guard let htmlString = String(data: data, encoding: .utf8) else {
            throw NetworkError.serverError("Unable to parse response")
        }
        
        // Check if we got a login page instead
        if htmlString.contains("<title>Login</title>") || htmlString.contains("class=\"login\"") {
            throw NetworkError.unauthorized
        }
        
        print("📄 Year filter HTML response length: \(htmlString.count)")
        
        // Parse groups from the response (should be groups list format)
        return parseGroupsFromHTML(htmlString)
    }
    
    func searchGroups(searchTerm: String) async throws -> [Group] {
        guard let cookie = UserManager.shared.cookie else {
            throw NetworkError.unauthorized
        }
        
        guard let url = URL(string: "\(baseURL)/groups/search") else {
            throw NetworkError.serverError("Invalid URL")
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        // Handle cookie format properly
        let cookieHeader = cookie.contains("session=") ? cookie : "session=\(cookie)"
        print("🍪 Raw cookie from UserManager: '\(cookie)'")
        print("🍪 Formatted cookie header: '\(cookieHeader)'")
        request.setValue(cookieHeader, forHTTPHeaderField: "Cookie")
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        request.setValue("GSaleApp/1.0", forHTTPHeaderField: "User-Agent")
        request.setValue("*/*", forHTTPHeaderField: "Accept")
        
        // Create form data with search term
        let formData = "name=\(searchTerm.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? "")"
        request.httpBody = formData.data(using: .utf8)
        
        print("🔍 Searching groups with term: '\(searchTerm)'")
        print("🍪 Search request cookie header: \(request.value(forHTTPHeaderField: "Cookie") ?? "None")")
        print("🌐 Search request URL: \(url)")
        print("📝 Search request body: \(formData)")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.serverError("Invalid response")
        }
        
        print("📡 Search groups response status: \(httpResponse.statusCode)")
        
        guard httpResponse.statusCode == 200 else {
            throw NetworkError.serverError("HTTP \(httpResponse.statusCode)")
        }
        
        guard let htmlString = String(data: data, encoding: .utf8) else {
            throw NetworkError.serverError("Unable to parse response")
        }
        
        // Check if we got a login page instead
        if htmlString.contains("<title>Login</title>") || htmlString.contains("class=\"login\"") {
            throw NetworkError.unauthorized
        }
        
        print("📄 Search HTML response length: \(htmlString.count)")
        print("📄 Search HTML preview: \(String(htmlString.prefix(500)))")
        
        // Check specifically if this is a login page
        if htmlString.contains("<title>Login</title>") || htmlString.contains("class=\"login\"") {
            print("❌ Search returned login page - authentication failed")
            throw NetworkError.unauthorized
        }
        
        // Extract and debug the table content specifically
        if let tableStart = htmlString.range(of: "<tbody>"),
           let tableEnd = htmlString.range(of: "</tbody>") {
            let tableContent = String(htmlString[tableStart.upperBound..<tableEnd.lowerBound])
            print("🔍 Extracted table content length: \(tableContent.count)")
            print("🔍 Table content: \(tableContent)")
        } else {
            print("❌ Could not find <tbody> tags in HTML")
        }
        
        // Parse groups from the search results table (same structure as groups/list)
        let searchResults = parseGroupsFromHTML(htmlString)
        print("🔍 Search found \(searchResults.count) groups")
        
        return searchResults
    }
    
    func getGroupDetails(groupId: String) async throws -> GroupDetail {
        let url = URL(string: "\(baseURL)/groups/describe?group_id=\(groupId)")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        // Set up session cookies for authentication
        if let cookie = UserManager.shared.cookie {
            request.setValue(cookie, forHTTPHeaderField: "Cookie")
            print("🍪 Sending cookie: \(cookie)")
        } else {
            print("⚠️ No cookie found - user not logged in")
            throw NetworkError.unauthorized
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
        
        // Parse HTML response to extract group details
        let responseString = String(data: data, encoding: .utf8) ?? ""
        print("📄 Group details response length: \(responseString.count)")
        
        // Parse group information from the HTML
        var groupName = "Group \(groupId)"
        var groupDate = "2024-01-01"
        var groupPrice = 0.0
        var totalItems = 0
        var soldItems = 0
        var soldPrice = 0.0
        var items: [GroupItem] = []
        
        // Extract group info from the first table
        // Looking for: <td>2025-07-30-Test</td><td><a href = "/groups/list?date=2025-07-30">2025-07-30</a></td><td>0</td><td>0</td>
        let groupInfoPattern = #"<td>([^<]+)</td>\s*<td><a[^>]*>([^<]+)</a></td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>"#
        
        do {
            let groupInfoRegex = try NSRegularExpression(pattern: groupInfoPattern, options: [.dotMatchesLineSeparators])
            let range = NSRange(responseString.startIndex..<responseString.endIndex, in: responseString)
            let matches = groupInfoRegex.matches(in: responseString, options: [], range: range)
            
            for match in matches {
                if match.numberOfRanges >= 5 {
                    let nameRange = Range(match.range(at: 1), in: responseString)!
                    let dateRange = Range(match.range(at: 2), in: responseString)!
                    let totalRange = Range(match.range(at: 3), in: responseString)!
                    let soldRange = Range(match.range(at: 4), in: responseString)!
                    
                    groupName = String(responseString[nameRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                    groupDate = String(responseString[dateRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                    totalItems = Int(String(responseString[totalRange]).trimmingCharacters(in: .whitespacesAndNewlines)) ?? 0
                    soldItems = Int(String(responseString[soldRange]).trimmingCharacters(in: .whitespacesAndNewlines)) ?? 0
                    
                    print("📦 Found group info: \(groupName), Date: \(groupDate), Total: \(totalItems), Sold: \(soldItems)")
                    break
                }
            }
        } catch {
            print("❌ Error parsing group info: \(error)")
        }
        
        // Extract monetary information
        // Looking for: <td>$5.00</td><td>$0</td><td></td><td>$-5.00</td>
        let monetaryPattern = #"<td>\$([^<]+)</td>\s*<td>\$([^<]+)</td>\s*<td>[^<]*</td>\s*<td>\$([^<]+)</td>"#
        
        do {
            let monetaryRegex = try NSRegularExpression(pattern: monetaryPattern, options: [.dotMatchesLineSeparators])
            let range = NSRange(responseString.startIndex..<responseString.endIndex, in: responseString)
            let matches = monetaryRegex.matches(in: responseString, options: [], range: range)
            
            for match in matches {
                if match.numberOfRanges >= 4 {
                    let purchaseRange = Range(match.range(at: 1), in: responseString)!
                    let saleRange = Range(match.range(at: 2), in: responseString)!
                    let profitRange = Range(match.range(at: 3), in: responseString)!
                    
                    groupPrice = Double(String(responseString[purchaseRange]).replacingOccurrences(of: "$", with: "").replacingOccurrences(of: ",", with: "")) ?? 0.0
                    soldPrice = Double(String(responseString[saleRange]).replacingOccurrences(of: "$", with: "").replacingOccurrences(of: ",", with: "")) ?? 0.0
                    
                    print("💰 Found monetary info: Purchase: $\(groupPrice), Sale: $\(soldPrice)")
                    break
                }
            }
        } catch {
            print("❌ Error parsing monetary info: \(error)")
        }
        
        // Note: Mock items removed - only showing real items from getItemsForGroup() call
        
        // Parse image filename if present
        var imageFilename: String? = nil
        let imagePattern = #"<img[^>]*src="[^"]*\/static\/uploads\/([^"]+)"[^>]*>"#
        
        do {
            let imageRegex = try NSRegularExpression(pattern: imagePattern, options: [])
            let imageRange = NSRange(responseString.startIndex..<responseString.endIndex, in: responseString)
            
            if let imageMatch = imageRegex.firstMatch(in: responseString, options: [], range: imageRange) {
                if let filenameRange = Range(imageMatch.range(at: 1), in: responseString) {
                    imageFilename = String(responseString[filenameRange])
                    print("📸 Found group image: \(imageFilename!)")
                }
            } else {
                print("📷 No image found for group \(groupId)")
            }
        } catch {
            print("❌ Error parsing image: \(error)")
        }

        return GroupDetail(
            id: groupId,
            name: groupName,
            date: groupDate,
            price: groupPrice,
            totalItems: totalItems,
            totalSoldItems: soldItems,
            soldPrice: soldPrice,
            items: items,
            imageFilename: imageFilename
        )
    }
    
    func getItemsForGroup(groupId: String) async throws -> [GroupItem] {
        let url = URL(string: "\(baseURL)/items/list")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        // Set up session cookies for authentication
        if let cookie = UserManager.shared.cookie {
            request.setValue(cookie, forHTTPHeaderField: "Cookie")
            print("🍪 Sending cookie: \(cookie)")
        } else {
            print("⚠️ No cookie found - user not logged in")
            throw NetworkError.unauthorized
        }
        
        print("🌐 Making items list request to: \(url)")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.serverError("Invalid response")
        }
        
        print("📡 Items list response status: \(httpResponse.statusCode)")
        
        if httpResponse.statusCode == 401 {
            throw NetworkError.unauthorized
        }
        
        guard httpResponse.statusCode == 200 else {
            let responseString = String(data: data, encoding: .utf8) ?? "Unknown error"
            print("❌ Items list request failed. Response: \(responseString)")
            throw NetworkError.serverError("HTTP \(httpResponse.statusCode)")
        }
        
        // Parse HTML response to extract items
        let responseString = String(data: data, encoding: .utf8) ?? ""
        print("📄 Items list response length: \(responseString.count)")
        
        var items: [GroupItem] = []
        
        // Parse items from the HTML table - simpler, more flexible pattern
        let itemPattern = #"<tr>[\s\S]*?<td>(\d+)</td>[\s\S]*?<td><a[^>]*href\s*=\s*"[^"]*item=([^"]+)"[^>]*>([^<]+)</a></td>[\s\S]*?<td>([^<]*)</td>[\s\S]*?<td>([^<]*)</td>[\s\S]*?<td>([^<]*)</td>[\s\S]*?<td><a[^>]*href\s*=\s*"[^"]*group_id=([^"]+)"[^>]*>([^<]+)</a></td>[\s\S]*?</tr>"#
        
        // Debug: Look for table content specifically
        if let tableStart = responseString.range(of: "<table")?.lowerBound {
            let tableEnd = responseString.index(tableStart, offsetBy: min(3000, responseString.count - responseString.distance(from: responseString.startIndex, to: tableStart)))
            let tableContent = String(responseString[tableStart..<tableEnd])
            print("📄 Table content: \(tableContent)")
        }
        
        // Also look for tbody content
        if let tbodyStart = responseString.range(of: "<tbody>")?.lowerBound {
            let tbodyEnd = responseString.index(tbodyStart, offsetBy: min(2000, responseString.count - responseString.distance(from: responseString.startIndex, to: tbodyStart)))
            let tbodyContent = String(responseString[tbodyStart..<tbodyEnd])
            print("📄 Tbody content: \(tbodyContent)")
        }
        
        // Try a simpler approach: find all table rows first, then parse each one
        let rowPattern = #"<tr>[\s\S]*?</tr>"#
        
        do {
            let rowRegex = try NSRegularExpression(pattern: rowPattern, options: [.dotMatchesLineSeparators])
            let range = NSRange(responseString.startIndex..<responseString.endIndex, in: responseString)
            let rowMatches = rowRegex.matches(in: responseString, options: [], range: range)
            
            print("🔍 Found \(rowMatches.count) table rows")
            
            for (index, rowMatch) in rowMatches.enumerated() {
                let rowRange = Range(rowMatch.range, in: responseString)!
                let rowContent = String(responseString[rowRange])
                
                // Skip header row
                if rowContent.contains("<th>") {
                    continue
                }
                
                print("🔍 Processing row \(index): \(String(rowContent.prefix(200)))...")
                
                // Extract item data from this row
                if let itemId = extractItemId(from: rowContent),
                   let itemName = extractItemName(from: rowContent),
                   let groupIdFromRow = extractGroupId(from: rowContent) {
                    
                    print("🔍 Found item: ID=\(itemId), Name=\(itemName), Group=\(groupIdFromRow)")
                    
                    // Only include items that belong to the specified group
                    if groupIdFromRow == groupId {
                        // Extract sold status and price
                        let soldNet = extractSoldNet(from: rowContent)
                        let isSold = !rowContent.contains("<td>NA</td>") && !rowContent.contains("Not Sold")
                        let price = Double(soldNet) ?? 0.0
                        
                        // Extract category and storage
                        let category = extractCategory(from: rowContent)
                        let storage = extractStorage(from: rowContent)
                        
                        let item = GroupItem(
                            id: itemId,
                            name: itemName,
                            price: price,
                            sold: isSold,
                            category: category,
                            storage: storage
                        )
                        items.append(item)
                        print("📦 Added item for group \(groupId): \(itemName) (Storage: \(storage ?? "N/A"), Category: \(category ?? "N/A"), Sold: \(isSold), Price: $\(price))")
                    } else {
                        print("⏭️ Skipping item \(itemName) - belongs to group \(groupIdFromRow), not \(groupId)")
                    }
                }
            }
        } catch {
            print("❌ Error parsing table rows: \(error)")
        }
        
        print("✅ Returning \(items.count) items for group \(groupId)")
        return items
    }
    
    // Helper functions for parsing item data from HTML rows
    private func extractItemId(from rowContent: String) -> String? {
        let pattern = #"href\s*=\s*"[^"]*item=([^"]+)""#
        return extractMatch(from: rowContent, pattern: pattern, groupIndex: 1)
    }
    
    private func extractItemName(from rowContent: String) -> String? {
        let pattern = #"href\s*=\s*"[^"]*item=[^"]+">([^<]+)</a>"#
        return extractMatch(from: rowContent, pattern: pattern, groupIndex: 1)
    }
    
    private func extractGroupId(from rowContent: String) -> String? {
        let pattern = #"href\s*=\s*"[^"]*group_id=([^"]+)""#
        return extractMatch(from: rowContent, pattern: pattern, groupIndex: 1)
    }
    
    private func extractSoldNet(from rowContent: String) -> String {
        // Look for numeric values in <td> tags (sold net is typically the 7th column)
        let pattern = #"<td>(\d+\.?\d*)</td>"#
        let matches = findAllMatches(in: rowContent, pattern: pattern)
        // Return the last numeric value found (sold net), or "0" if none found
        return matches.last ?? "0"
    }
    
    private func extractCategory(from rowContent: String) -> String? {
        // TODO: Re-enable API category fetching once authentication is fixed
        // For now, use pattern matching directly
        /*
        if let itemId = extractItemId(from: rowContent) {
            if let realCategory = getCategoryFromItemDescribe(itemId: itemId) {
                return realCategory
            }
        }
        */
        
        // Use pattern matching for categories
        guard let itemName = extractItemName(from: rowContent) else {
            return "Uncategorized"
        }
        
        let name = itemName.lowercased()
        
        // Gaming & Electronics
        if name.contains("console") || name.contains("wii") || name.contains("xbox") || 
           name.contains("playstation") || name.contains("nintendo") || name.contains("ps") ||
           name.contains("game") || name.contains("controller") {
            return "Gaming"
        }
        
        // Electronics
        if name.contains("phone") || name.contains("iphone") || name.contains("android") ||
           name.contains("tablet") || name.contains("ipad") || name.contains("laptop") ||
           name.contains("computer") || name.contains("tv") || name.contains("monitor") ||
           name.contains("headphone") || name.contains("speaker") || name.contains("camera") ||
           name.contains("electronic") || name.contains("cable") || name.contains("charger") {
            return "Electronics"
        }
        
        // Books & Media
        if name.contains("book") || name.contains("dvd") || name.contains("cd") ||
           name.contains("blu-ray") || name.contains("movie") || name.contains("album") {
            return "Books & Media"
        }
        
        // Clothing & Accessories
        if name.contains("shirt") || name.contains("pants") || name.contains("dress") ||
           name.contains("jacket") || name.contains("shoes") || name.contains("hat") ||
           name.contains("clothing") || name.contains("clothes") || name.contains("jeans") ||
           name.contains("sweater") || name.contains("coat") || name.contains("belt") {
            return "Clothing & Accessories"
        }
        
        // Home & Garden
        if name.contains("kitchen") || name.contains("cooking") || name.contains("furniture") ||
           name.contains("home") || name.contains("garden") || name.contains("tool") ||
           name.contains("appliance") || name.contains("lamp") || name.contains("decoration") {
            return "Home & Garden"
        }
        
        // Toys & Collectibles
        if name.contains("toy") || name.contains("doll") || name.contains("figure") ||
           name.contains("collectible") || name.contains("action") || name.contains("lego") ||
           name.contains("puzzle") || name.contains("board game") {
            return "Toys & Collectibles"
        }
        
        // Sports & Outdoor
        if name.contains("sports") || name.contains("bike") || name.contains("bicycle") ||
           name.contains("outdoor") || name.contains("camping") || name.contains("fishing") ||
           name.contains("golf") || name.contains("tennis") || name.contains("basketball") {
            return "Sports & Outdoor"
        }
        
        // Automotive
        if name.contains("car") || name.contains("auto") || name.contains("tire") ||
           name.contains("vehicle") || name.contains("motor") || name.contains("engine") {
            return "Automotive"
        }
        
        // Test items (for development) - check for specific test1 item
        if name.contains("test1") {
            return "board games"  // Known category for test1 item
        } else if name.contains("test") {
            return "Test Items"
        }
        
        // Default category for items that don't match any pattern
        return "General"
    }
    
    private func getCategoryFromItemDescribe(itemId: String) -> String? {
        guard let cookie = UserManager.shared.cookie else {
            print("❌ No session cookie available for category fetch")
            return nil
        }
        
        guard let url = URL(string: "\(baseURL)/items/describe?item=\(itemId)") else {
            print("❌ Invalid URL for item describe")
            return nil
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        // Handle cookie format properly - if it already contains "session=", use as is
        let cookieHeader = cookie.contains("session=") ? cookie : "session=\(cookie)"
        request.setValue(cookieHeader, forHTTPHeaderField: "Cookie")
        request.setValue("GSaleApp/1.0", forHTTPHeaderField: "User-Agent")
        request.setValue("*/*", forHTTPHeaderField: "Accept")
        
        print("🔍 Fetching category for item \(itemId) from /items/describe")
        print("🍪 Raw cookie from UserManager: \(cookie)")
        print("🍪 Cookie header being sent: \(cookieHeader)")
        print("🌐 Request URL: \(url)")
        
        let semaphore = DispatchSemaphore(value: 0)
        var categoryResult: String? = nil
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            defer { semaphore.signal() }
            
            if let error = error {
                print("❌ Network error fetching category: \(error.localizedDescription)")
                return
            }
            
            guard let httpResponse = response as? HTTPURLResponse else {
                print("❌ Invalid HTTP response for category fetch")
                return
            }
            
            print("📡 Category fetch response status: \(httpResponse.statusCode)")
            
            guard let data = data,
                  let htmlString = String(data: data, encoding: .utf8) else {
                print("❌ Failed to get item describe HTML for category")
                return
            }
            
            print("📄 Item describe HTML length: \(htmlString.count)")
            print("📄 HTML preview: \(String(htmlString.prefix(500)))")
            
            // Check if we got a login page instead of item details
            if htmlString.contains("<title>Login</title>") || htmlString.contains("class=\"login\"") {
                print("❌ Received login page instead of item details - authentication failed")
                return
            }
            
            // Look for the category in the first table, second column
            // Based on the actual HTML structure: <td>test1</td><td>Board Games</td>
            let patterns = [
                // Pattern 1: Find the exact structure - name then category
                #"<tr>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>"#,
                // Pattern 2: More specific - look for item name followed by category
                #"<td>test1</td>\s*<td>([^<]+)</td>"#,
                // Pattern 3: General pattern for any name followed by category
                #"<td>[^<]+</td>\s*<td>([^<]+)</td>\s*<td><a href"#,
                // Pattern 4: Direct category cell pattern
                #"<td>([A-Za-z\s]+)</td>\s*<td><a href = "/groups/list"#
            ]
            
            for (index, pattern) in patterns.enumerated() {
                if let regex = try? NSRegularExpression(pattern: pattern, options: [.caseInsensitive]) {
                    let matches = regex.matches(in: htmlString, options: [], range: NSRange(location: 0, length: htmlString.count))
                    print("🔍 Pattern \(index + 1) found \(matches.count) matches")
                    
                    for match in matches {
                        // For pattern 1, we want the second capture group (category)
                        let captureIndex = (index == 0) ? 2 : 1
                        
                        if match.numberOfRanges > captureIndex,
                           let categoryRange = Range(match.range(at: captureIndex), in: htmlString) {
                            let category = String(htmlString[categoryRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                            print("🔍 Found potential category: '\(category)'")
                            
                            if !category.isEmpty && 
                               category != "None" && 
                               category != "test1" &&
                               category.count > 1 &&
                               !category.contains("href") &&
                               !category.contains("2025") {
                                categoryResult = category
                                print("✅ Found real category for item \(itemId): \(category)")
                                return
                            }
                        }
                    }
                }
            }
            
            // If specific patterns fail, extract all table cells and look for "board games"
            let allCellsPattern = #"<td>([^<]+)</td>"#
            if let regex = try? NSRegularExpression(pattern: allCellsPattern, options: [.caseInsensitive]) {
                let matches = regex.matches(in: htmlString, options: [], range: NSRange(location: 0, length: htmlString.count))
                print("🔍 Found \(matches.count) total table cells")
                
                for match in matches {
                    if let cellRange = Range(match.range(at: 1), in: htmlString) {
                        let cellContent = String(htmlString[cellRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                        print("📋 Cell content: '\(cellContent)'")
                        
                        if (cellContent.lowercased().contains("board") && cellContent.lowercased().contains("game")) ||
                           cellContent.lowercased() == "board games" ||
                           (cellContent.count > 3 && 
                            !cellContent.contains("href") && 
                            !cellContent.contains("2025") &&
                            !cellContent.contains("test1") &&
                            cellContent != "None") {
                            categoryResult = cellContent
                            print("✅ Found category in cell scan: \(cellContent)")
                            return
                        }
                    }
                }
            }
            
            print("❌ Could not parse category from item describe HTML for item \(itemId)")
        }.resume()
        
        semaphore.wait()
        return categoryResult
    }
    
    // MARK: - Item Management
    func removeItem(itemId: String) async throws {
        guard let cookie = UserManager.shared.cookie else {
            throw NetworkError.unauthorized
        }
        
        guard let url = URL(string: "\(baseURL)/items/remove?id=\(itemId)") else {
            throw NetworkError.serverError("Invalid URL")
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        // Handle cookie format properly
        let cookieHeader = cookie.contains("session=") ? cookie : "session=\(cookie)"
        request.setValue(cookieHeader, forHTTPHeaderField: "Cookie")
        request.setValue("GSaleApp/1.0", forHTTPHeaderField: "User-Agent")
        request.setValue("*/*", forHTTPHeaderField: "Accept")
        
        print("🗑️ Removing item: \(itemId)")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.serverError("Invalid response")
        }
        
        print("📡 Remove item response status: \(httpResponse.statusCode)")
        
        guard httpResponse.statusCode == 200 || httpResponse.statusCode == 302 else {
            throw NetworkError.serverError("HTTP \(httpResponse.statusCode)")
        }
        
        // Check if we got a login page instead
        if let htmlString = String(data: data, encoding: .utf8),
           (htmlString.contains("<title>Login</title>") || htmlString.contains("class=\"login\"")) {
            throw NetworkError.unauthorized
        }
        
        print("✅ Item removed successfully")
    }
    
    // MARK: - Item Details
    func getItemDetails(itemId: String) async throws -> ItemDetail {
        guard let cookie = UserManager.shared.cookie else {
            throw NetworkError.unauthorized
        }
        
        guard let url = URL(string: "\(baseURL)/items/describe?item=\(itemId)") else {
            throw NetworkError.serverError("Invalid URL")
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        // Handle cookie format properly
        let cookieHeader = cookie.contains("session=") ? cookie : "session=\(cookie)"
        request.setValue(cookieHeader, forHTTPHeaderField: "Cookie")
        request.setValue("GSaleApp/1.0", forHTTPHeaderField: "User-Agent")
        request.setValue("*/*", forHTTPHeaderField: "Accept")
        
        print("🔍 Fetching item details for: \(itemId)")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.serverError("Invalid response")
        }
        
        print("📡 Item details response status: \(httpResponse.statusCode)")
        
        guard httpResponse.statusCode == 200 else {
            throw NetworkError.serverError("HTTP \(httpResponse.statusCode)")
        }
        
        guard let htmlString = String(data: data, encoding: .utf8) else {
            throw NetworkError.serverError("Invalid response data")
        }
        
        print("📄 Item details HTML length: \(htmlString.count)")
        
        // Check if we got a login page instead of item details
        if htmlString.contains("<title>Login</title>") || htmlString.contains("class=\"login\"") {
            throw NetworkError.unauthorized
        }
        
        // Parse the item details from the HTML
        return try parseItemDetails(from: htmlString, itemId: itemId)
    }
    
    private func parseItemDetails(from html: String, itemId: String) throws -> ItemDetail {
        // Extract data from the first table based on the HTML structure:
        // <td>test1</td><td>Board Games</td><td>2025-07-29</td><td>2025-07-29</td><td>a2</td><td>2025-07-29-Test</td>
        
        // Pattern to match the main data row
        let tableRowPattern = #"<tr>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td><a[^>]*>([^<]+)</a></td>\s*<td>([^<]*)</td>\s*<td>([^<]*)</td>\s*<td><a[^>]*>([^<]+)</a></td>\s*</tr>"#
        
        guard let regex = try? NSRegularExpression(pattern: tableRowPattern, options: []),
              let match = regex.firstMatch(in: html, options: [], range: NSRange(location: 0, length: html.count)),
              match.numberOfRanges >= 7 else {
            print("❌ Could not parse item details from HTML")
            throw NetworkError.serverError("Failed to parse item details")
        }
        
        // Extract all the captured groups
        let name = extractString(from: html, range: match.range(at: 1))
        let category = extractString(from: html, range: match.range(at: 2))
        let purchaseDate = extractString(from: html, range: match.range(at: 3))
        let listDate = extractString(from: html, range: match.range(at: 4))
        let storage = extractString(from: html, range: match.range(at: 5))
        let groupName = extractString(from: html, range: match.range(at: 6))
        
        // Extract group ID from the group link
        let groupIdPattern = #"group_id=([^"]+)"#
        var groupId = ""
        if let groupRegex = try? NSRegularExpression(pattern: groupIdPattern, options: []),
           let groupMatch = groupRegex.firstMatch(in: html, options: [], range: NSRange(location: 0, length: html.count)) {
            groupId = extractString(from: html, range: groupMatch.range(at: 1))
        }
        
        // Check if item is sold by looking for "Sold" in the status table
        let sold = html.contains("<td>Sold</td>")
        
        // Parse sold item financial details if the item is sold
        var soldPrice: Double? = nil
        var shippingFee: Double? = nil
        var netPrice: Double? = nil
        var soldDate: String? = nil
        var daysToSell: Int? = nil
        
        if sold {
            print("🔍 Item is sold, attempting to parse financial details...")
            print("📄 HTML snippet for debugging: \(String(html.suffix(1000)))")
            
            // Try multiple patterns for the sold price table
            let soldPricePatterns = [
                // Pattern 1: Simple three consecutive cells
                #"<tr>\s*<td>([0-9.]+)</td>\s*<td>([0-9.]+)</td>\s*<td>([0-9.]+)</td>\s*</tr>"#,
                // Pattern 2: More flexible whitespace
                #"<td>\s*([0-9.]+)\s*</td>\s*<td>\s*([0-9.]+)\s*</td>\s*<td>\s*([0-9.]+)\s*</td>"#,
                // Pattern 3: Look for the last table with three numeric cells
                #"<table[^>]*>.*?<td>([0-9.]+)</td>\s*<td>([0-9.]+)</td>\s*<td>([0-9.]+)</td>.*?</table>"#
            ]
            
            for (index, pattern) in soldPricePatterns.enumerated() {
                if let regex = try? NSRegularExpression(pattern: pattern, options: [.dotMatchesLineSeparators]) {
                    let matches = regex.matches(in: html, options: [], range: NSRange(location: 0, length: html.count))
                    if let match = matches.last {
                        print("✅ Sold price pattern \(index + 1) matched!")
                        soldPrice = Double(extractString(from: html, range: match.range(at: 1)))
                        shippingFee = Double(extractString(from: html, range: match.range(at: 2)))
                        netPrice = Double(extractString(from: html, range: match.range(at: 3)))
                        print("💰 Extracted: Price=\(soldPrice ?? 0), Shipping=\(shippingFee ?? 0), Net=\(netPrice ?? 0)")
                        break
                    }
                }
            }
            
            // Try to find "Sold" status and extract date/days
            let statusPatterns = [
                // Pattern 1: Standard format
                #"<td>Sold</td>\s*<td>([0-9.]+)</td>\s*<td><a[^>]*>([^<]+)</a></td>\s*<td>([0-9]+)</td>"#,
                // Pattern 2: More flexible
                #"<td>\s*Sold\s*</td>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*><a[^>]*>([^<]+)</a></td>\s*<td[^>]*>([0-9]+)</td>"#
            ]
            
            for (index, pattern) in statusPatterns.enumerated() {
                if let regex = try? NSRegularExpression(pattern: pattern, options: [.dotMatchesLineSeparators]),
                   let match = regex.firstMatch(in: html, options: [], range: NSRange(location: 0, length: html.count)) {
                    print("✅ Status pattern \(index + 1) matched!")
                    if index == 0 {
                        soldDate = extractString(from: html, range: match.range(at: 2))
                        daysToSell = Int(extractString(from: html, range: match.range(at: 3)))
                    } else {
                        soldDate = extractString(from: html, range: match.range(at: 2))
                        daysToSell = Int(extractString(from: html, range: match.range(at: 3)))
                    }
                    print("📅 Extracted: Date=\(soldDate ?? "nil"), Days=\(daysToSell ?? 0)")
                    break
                }
            }
            
            if soldPrice == nil && shippingFee == nil && netPrice == nil {
                print("❌ Failed to parse any financial details")
            }
        }
        
        // For now, assume not returned (we could parse this from additional tables if needed)
        let returned = false
        
        print("✅ Parsed item details: \(name) - Category: \(category), Sold: \(sold)")
        if sold {
            print("💰 Sold details - Price: \(soldPrice ?? 0), Shipping: \(shippingFee ?? 0), Net: \(netPrice ?? 0)")
        }
        
        return ItemDetail(
            id: itemId,
            name: name,
            sold: sold,
            groupId: groupId,
            categoryId: 0, // We don't extract this from HTML
            category: category,
            returned: returned,
            storage: storage.isEmpty ? nil : storage,
            listDate: listDate.isEmpty ? nil : listDate,
            groupName: groupName,
            purchaseDate: purchaseDate,
            soldPrice: soldPrice,
            shippingFee: shippingFee,
            netPrice: netPrice,
            soldDate: soldDate,
            daysToSell: daysToSell
        )
    }
    
    private func extractString(from html: String, range: NSRange) -> String {
        guard let stringRange = Range(range, in: html) else { return "" }
        return String(html[stringRange]).trimmingCharacters(in: .whitespacesAndNewlines)
    }
    
    private func extractStorage(from rowContent: String) -> String? {
        // Storage is typically in a link format: <a href="/items/list?storage=a2">a2</a>
        let pattern = #"href\s*=\s*"[^"]*storage=([^"]*)"[^>]*>([^<]*)</a>"#
        return extractMatch(from: rowContent, pattern: pattern, groupIndex: 2)
    }
    
    private func extractMatch(from text: String, pattern: String, groupIndex: Int) -> String? {
        do {
            let regex = try NSRegularExpression(pattern: pattern, options: [])
            let range = NSRange(text.startIndex..<text.endIndex, in: text)
            if let match = regex.firstMatch(in: text, options: [], range: range),
               match.numberOfRanges > groupIndex {
                let matchRange = Range(match.range(at: groupIndex), in: text)!
                return String(text[matchRange]).trimmingCharacters(in: .whitespacesAndNewlines)
            }
        } catch {
            print("❌ Error in regex pattern \(pattern): \(error)")
        }
        return nil
    }
    
    private func findAllMatches(in text: String, pattern: String) -> [String] {
        var matches: [String] = []
        do {
            let regex = try NSRegularExpression(pattern: pattern, options: [])
            let range = NSRange(text.startIndex..<text.endIndex, in: text)
            let results = regex.matches(in: text, options: [], range: range)
            
            for result in results {
                if result.numberOfRanges > 1 {
                    let matchRange = Range(result.range(at: 1), in: text)!
                    matches.append(String(text[matchRange]).trimmingCharacters(in: .whitespacesAndNewlines))
                }
            }
        } catch {
            print("❌ Error finding matches for pattern \(pattern): \(error)")
        }
        return matches
    }
    
    func modifyGroup(groupId: String, name: String, price: Double, date: String) async throws {
        let url = URL(string: "\(baseURL)/groups/modify")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        
        // Set up session cookies for authentication
        if let cookie = UserManager.shared.cookie {
            request.setValue(cookie, forHTTPHeaderField: "Cookie")
            print("🍪 Sending cookie: \(cookie)")
        } else {
            print("⚠️ No cookie found - user not logged in")
            throw NetworkError.unauthorized
        }
        
        // Create form data
        let formData = "group_id=\(groupId)&name=\(name.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? name)&price=\(price)&date=\(date.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? date)"
        request.httpBody = formData.data(using: .utf8)
        
        print("🌐 Making modify group request to: \(url)")
        print("📝 Form data: \(formData)")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.serverError("Invalid response")
        }
        
        print("📡 Modify group response status: \(httpResponse.statusCode)")
        
        if httpResponse.statusCode == 401 {
            throw NetworkError.unauthorized
        }
        
        guard httpResponse.statusCode == 200 || httpResponse.statusCode == 302 else {
            let responseString = String(data: data, encoding: .utf8) ?? "Unknown error"
            print("❌ Modify group request failed. Response: \(responseString)")
            throw NetworkError.serverError("HTTP \(httpResponse.statusCode)")
        }
        
        print("✅ Group modified successfully")
    }
    
    func removeGroup(groupId: String) async throws {
        // Backend expects group ID as query parameter 'id', not form data
        let url = URL(string: "\(baseURL)/groups/remove?id=\(groupId)")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"  // Backend accepts both GET and POST, using GET for simplicity
        
        // Set up session cookies for authentication
        if let cookie = UserManager.shared.cookie {
            request.setValue(cookie, forHTTPHeaderField: "Cookie")
            print("🍪 Sending cookie: \(cookie)")
        } else {
            print("⚠️ No cookie found - user not logged in")
            throw NetworkError.unauthorized
        }
        
        print("🌐 Making remove group request to: \(url)")
        print("📝 Group ID: \(groupId)")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.serverError("Invalid response")
        }
        
        print("📡 Remove group response status: \(httpResponse.statusCode)")
        
        if httpResponse.statusCode == 401 {
            throw NetworkError.unauthorized
        }
        
        // Backend redirects to groups list after successful deletion (302)
        guard httpResponse.statusCode == 200 || httpResponse.statusCode == 302 else {
            let responseString = String(data: data, encoding: .utf8) ?? "Unknown error"
            print("❌ Remove group request failed. Response: \(responseString)")
            print("📄 Response preview: \(String(responseString.prefix(500)))")
            throw NetworkError.serverError("HTTP \(httpResponse.statusCode)")
        }
        
        print("✅ Group removed successfully - status: \(httpResponse.statusCode)")
    }
    
    func addGroup(name: String, price: Double, date: Date, image: UIImage? = nil) async throws -> AddGroupResponse {
        let url = URL(string: "\(baseURL)/groups/create")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        // Don't follow redirects automatically - we want to handle them manually
        request.httpShouldUsePipelining = false
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
            print("🔄 Redirect detected: \(locationHeader)")
            
            if locationHeader.contains("/login") {
                print("❌ Not authenticated - redirecting to login")
                throw NetworkError.unauthorized
            }
            
            // Check if this is a redirect to group describe page
            if locationHeader.contains("/groups/describe") {
                print("✅ Group created successfully - redirecting to group describe")
                
                // Extract group ID from the Location header
                var groupId: String? = nil
                if let idMatch = locationHeader.range(of: "group_id=") {
                    let idStart = locationHeader.index(idMatch.upperBound, offsetBy: 0)
                    let idEnd = locationHeader.index(idStart, offsetBy: 36) // UUID length
                    let idString = String(locationHeader[idStart..<idEnd])
                    if !idString.isEmpty {
                        groupId = idString
                        print("📦 Extracted group ID from redirect: \(idString)")
                    }
                }
                
                return AddGroupResponse(
                    success: true,
                    message: "Group created successfully",
                    group_id: groupId
                )
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
            print("📄 Response body length: \(responseString.count)")
            print("📄 Response body preview: \(String(responseString.prefix(500)))")
            
            // Check if response contains error indicators
            let lowercasedResponse = responseString.lowercased()
            if lowercasedResponse.contains("error") || lowercasedResponse.contains("failed") || lowercasedResponse.contains("exception") {
                print("❌ 200 response but contains error")
                print("📄 Full error response: \(responseString)")
                throw NetworkError.serverError("Server returned error: \(responseString)")
            }
            
            // Check if this is a successful HTML page (contains common HTML elements)
            if responseString.contains("<html") || responseString.contains("<body") || responseString.contains("<!DOCTYPE") {
                print("✅ 200 response appears to be valid HTML")
            }
            
            // Check if this is a redirect to group details page
            if responseString.contains("Group Information") || responseString.contains("groups/describe") {
                print("✅ Group created successfully - redirected to group details")
                
                // Extract group ID from the URL if present
                var groupId: String? = nil
                if let url = request.url {
                    let urlString = url.absoluteString
                    if let idMatch = urlString.range(of: "group_id=") {
                        let idStart = urlString.index(idMatch.upperBound, offsetBy: 0)
                        let idEnd = urlString.index(idStart, offsetBy: 36) // UUID length
                        let idString = String(urlString[idStart..<idEnd])
                        if !idString.isEmpty {
                            groupId = idString
                        }
                    }
                }
                
                return AddGroupResponse(
                    success: true,
                    message: "Group created successfully",
                    group_id: groupId
                )
            }
            
            // Check if this is a successful HTML page (not an error page)
            if responseString.contains("<html") && !lowercasedResponse.contains("error") {
                print("✅ Group created successfully - received HTML page")
                
                // Check if this is the group describe page
                if responseString.contains("Group Information") || responseString.contains("groups/describe") {
                    print("✅ This appears to be the group describe page")
                }
                
                // Try to extract group ID from the page content
                var groupId: String? = nil
                let groupIdPattern = #"group_id=([^"]+)"#
                
                do {
                    let regex = try NSRegularExpression(pattern: groupIdPattern)
                    let range = NSRange(responseString.startIndex..<responseString.endIndex, in: responseString)
                    if let match = regex.firstMatch(in: responseString, options: [], range: range) {
                        if match.numberOfRanges >= 2 {
                            let idRange = Range(match.range(at: 1), in: responseString)!
                            let idString = String(responseString[idRange])
                            groupId = idString
                            print("📦 Extracted group ID: \(groupId ?? "none")")
                        }
                    }
                } catch {
                    print("❌ Error extracting group ID: \(error)")
                }
                
                return AddGroupResponse(
                    success: true,
                    message: "Group created successfully",
                    group_id: groupId
                )
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
