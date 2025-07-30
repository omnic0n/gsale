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
            // Use the captured cookie from the delegate
            let sessionCookie = delegate.capturedCookie ?? "session=logged_in"
            
            // Login successful - create a response
            let loginResponse = LoginResponse(
                success: true,
                message: "Login successful",
                cookie: sessionCookie,
                user_id: nil,
                username: username,
                is_admin: false
            )
            
            print("🔐 Login successful - cookie: \(sessionCookie)")
            return loginResponse
        }
        
        // If we get here, login failed
        let responseString = String(data: data, encoding: .utf8) ?? "Unknown error"
        print("❌ Login failed. Status: \(httpResponse.statusCode)")
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
                   print("🍪 Sending cookie: \(cookie)")
               } else {
                   print("⚠️ No cookie found - user not logged in")
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
               
               // Debug: Print first 1000 characters to see the structure
               if responseString.count > 1000 {
                   print("📄 First 1000 chars: \(String(responseString.prefix(1000)))")
               } else {
                   print("📄 Full response: \(responseString)")
               }
               
               // Debug: Check if this looks like a login page
               if responseString.contains("login") || responseString.contains("Login") {
                   print("⚠️ Response appears to be a login page - user may not be authenticated")
                   print("📄 Login page content: \(String(responseString.prefix(500)))")
                   throw NetworkError.unauthorized
               }
               
               // Debug: Check if this looks like an error page
               if responseString.contains("error") || responseString.contains("Error") {
                   print("⚠️ Response appears to be an error page")
               }
               
               // Debug: Look for specific patterns in the HTML
               if responseString.contains("blueTable") {
                   print("✅ Found blueTable class (groups table)")
               }
               if responseString.contains("groups/describe") {
                   print("✅ Found groups/describe links")
               }
               if responseString.contains("group_id=") {
                   print("✅ Found group_id parameters")
               }
               
               // Debug: Show a sample of the HTML to understand the structure
               if let sampleStart = responseString.range(of: "<tbody>")?.lowerBound {
                   let sampleEnd = responseString.index(sampleStart, offsetBy: min(1000, responseString.count - responseString.distance(from: responseString.startIndex, to: sampleStart)))
                   let sample = String(responseString[sampleStart..<sampleEnd])
                   print("📄 HTML sample starting from <tbody>: \(sample)")
               }
               
               // Debug: Look for specific patterns in the HTML
               if responseString.contains("blueTable") {
                   print("✅ Found blueTable class (groups table)")
               }
               if responseString.contains("groups/describe") {
                   print("✅ Found groups/describe links")
               }
               if responseString.contains("group_id=") {
                   print("✅ Found group_id parameters")
               }
               
               // Debug: Show a sample of the HTML to understand the structure
               if let sampleStart = responseString.range(of: "<tbody>")?.lowerBound {
                   let sampleEnd = responseString.index(sampleStart, offsetBy: min(1000, responseString.count - responseString.distance(from: responseString.startIndex, to: sampleStart)))
                   let sample = String(responseString[sampleStart..<sampleEnd])
                   print("📄 HTML sample starting from <tbody>: \(sample)")
               }
               
               // Extract groups from HTML table
               var groups: [Group] = []
               
               print("🔍 Starting HTML parsing...")
               print("📄 HTML length: \(responseString.count)")
               
               // Parse the HTML table to extract complete group information
               // Looking for: <td>count</td><td><a href="/groups/describe?group_id=uuid">name</td><td>total</td><td>sold</td>...
               let groupRowPattern = #"<td>(\d+)</td>\s*<td><a[^>]*href="[^"]*group_id=([^"]+)"[^>]*>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>"#
               
               do {
                   let regex = try NSRegularExpression(pattern: groupRowPattern, options: [.dotMatchesLineSeparators])
                   let range = NSRange(responseString.startIndex..<responseString.endIndex, in: responseString)
                   let matches = regex.matches(in: responseString, options: [], range: range)
                   
                   print("🔍 Found \(matches.count) potential group rows")
                   
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
                   print("❌ Error with regex: \(error)")
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
               
                               // If the simple parsing didn't work, try a fallback approach
                if groups.isEmpty {
                    print("🔄 Simple parsing found no groups, trying fallback...")
                    
                    // Look for any links with group_id in the entire HTML
                    let lines = responseString.components(separatedBy: .newlines)
                    for line in lines {
                        if line.contains("group_id=") && line.contains("</a>") {
                            print("🔍 Found potential group line: \(line)")
                            
                            // Extract group ID
                            if let groupIdMatch = line.range(of: "group_id=") {
                                let afterGroupId = String(line[groupIdMatch.upperBound...])
                                if let endQuote = afterGroupId.range(of: "\"")?.lowerBound {
                                    let groupIdStr = String(afterGroupId[..<endQuote])
                                    if !groupIdStr.isEmpty {
                                        print("📦 Found group ID: \(groupIdStr)")
                                        
                                        // Extract group name
                                        if let nameStart = line.range(of: ">", options: .backwards)?.upperBound,
                                           let nameEnd = line.range(of: "</a>")?.lowerBound {
                                            let name = String(line[nameStart..<nameEnd]).trimmingCharacters(in: .whitespacesAndNewlines)
                                            
                                            if !name.isEmpty && name != "Name" {
                                                let group = Group(
                                                    id: groupIdStr,
                                                    name: name,
                                                    description: nil,
                                                    created_at: "2024-01-01",
                                                    updated_at: "2024-01-01"
                                                )
                                                groups.append(group)
                                                print("✅ Added group (fallback): \(name) (ID: \(groupIdStr))")
                                            }
                                        }
                                    }
                                }
                            }
                        }
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
    
               func getGroupDetails(groupId: String) async throws -> GroupDetail {
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
               
               // Parse HTML response to extract group details
               let responseString = String(data: data, encoding: .utf8) ?? ""
               print("📄 Group details response length: \(responseString.count)")
               
               // Parse group information from the HTML
               var groupName = "Group \(String(groupId))"
               var groupDate = "2024-01-01"
               var groupPrice = 0.0
               var totalItems = 0
               var soldItems = 0
               var soldPrice = 0.0
               var items: [GroupItem] = []
               
               // Extract group info from the first table
               let groupInfoPattern = #"<td[^>]*>([^<]+)</td>\s*<td[^>]*>[^<]*<a[^>]*>([^<]+)</a></td>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>"#
               
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
               let monetaryPattern = #"<td[^>]*>\$([^<]+)</td>\s*<td[^>]*>\$([^<]+)</td>\s*<td[^>]*>[^<]*\$([^<]+)[^<]*</td>\s*<td[^>]*>\$([^<]+)</td>"#
               
               do {
                   let monetaryRegex = try NSRegularExpression(pattern: monetaryPattern, options: [.dotMatchesLineSeparators])
                   let range = NSRange(responseString.startIndex..<responseString.endIndex, in: responseString)
                   let matches = monetaryRegex.matches(in: responseString, options: [], range: range)
                   
                   for match in matches {
                       if match.numberOfRanges >= 5 {
                           let purchaseRange = Range(match.range(at: 1), in: responseString)!
                           let saleRange = Range(match.range(at: 2), in: responseString)!
                           let averageRange = Range(match.range(at: 3), in: responseString)!
                           let profitRange = Range(match.range(at: 4), in: responseString)!
                           
                           groupPrice = Double(String(responseString[purchaseRange]).replacingOccurrences(of: "$", with: "").replacingOccurrences(of: ",", with: "")) ?? 0.0
                           soldPrice = Double(String(responseString[saleRange]).replacingOccurrences(of: "$", with: "").replacingOccurrences(of: ",", with: "")) ?? 0.0
                           
                           print("💰 Found monetary info: Purchase: $\(groupPrice), Sale: $\(soldPrice)")
                           break
                       }
                   }
               } catch {
                   print("❌ Error parsing monetary info: \(error)")
               }
               
               // Extract items from the items table
               let itemPattern = #"<td[^>]*>([^<]+)</td>\s*<td[^>]*>[^<]*<a[^>]*>([^<]+)</a>[^<]*</td>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>"#
               
               do {
                   let itemRegex = try NSRegularExpression(pattern: itemPattern, options: [.dotMatchesLineSeparators])
                   let range = NSRange(responseString.startIndex..<responseString.endIndex, in: responseString)
                   let matches = itemRegex.matches(in: responseString, options: [], range: range)
                   
                   for match in matches {
                       if match.numberOfRanges >= 9 {
                           let countRange = Range(match.range(at: 1), in: responseString)!
                           let nameRange = Range(match.range(at: 2), in: responseString)!
                           let soldDateRange = Range(match.range(at: 3), in: responseString)!
                           let daysRange = Range(match.range(at: 4), in: responseString)!
                           let grossRange = Range(match.range(at: 5), in: responseString)!
                           let netRange = Range(match.range(at: 6), in: responseString)!
                           let shippingRange = Range(match.range(at: 7), in: responseString)!
                           let storageRange = Range(match.range(at: 8), in: responseString)!
                           
                           let count = String(responseString[countRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                           let name = String(responseString[nameRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                           let soldDate = String(responseString[soldDateRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                           let gross = String(responseString[grossRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                           let net = String(responseString[netRange]).trimmingCharacters(in: .whitespacesAndNewlines)
                           
                           // Skip header rows
                           if count.lowercased() == "name" || count.isEmpty {
                               continue
                           }
                           
                           let isSold = soldDate != "Not Sold"
                           let price = Double(net.replacingOccurrences(of: "$", with: "").replacingOccurrences(of: ",", with: "")) ?? 0.0
                           
                           let item = GroupItem(
                               id: String(items.count + 1),
                               name: name,
                               price: price,
                               sold: isSold
                           )
                           items.append(item)
                           print("📦 Found item: \(name), Sold: \(isSold), Price: $\(price)")
                       }
                   }
               } catch {
                   print("❌ Error parsing items: \(error)")
               }
               
               let groupDetail = GroupDetail(
                   id: groupId,
                   name: groupName,
                   date: groupDate,
                   price: groupPrice,
                   totalItems: totalItems,
                   totalSoldItems: soldItems,
                   soldPrice: soldPrice,
                   items: items
               )
               
               print("✅ Returning detailed group info for group \(groupId): \(groupName)")
               return groupDetail
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
                   
                   // Debug: Check for common HTML patterns
                   if responseString.contains("<html") {
                       print("✅ Response contains HTML")
                   }
                   if responseString.contains("form") {
                       print("✅ Response contains form")
                   }
                   if responseString.contains("Group") {
                       print("✅ Response contains 'Group'")
                   }
                   
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
                       
                       // If we couldn't extract from URL, try to find it in the page content
                       if groupId == nil {
                           let pageGroupIdPattern = #"group_id=(\d+)"#
                           do {
                               let regex = try NSRegularExpression(pattern: pageGroupIdPattern)
                               let range = NSRange(responseString.startIndex..<responseString.endIndex, in: responseString)
                               let matches = regex.matches(in: responseString, options: [], range: range)
                               
                               for match in matches {
                                   if match.numberOfRanges >= 2 {
                                       let idRange = Range(match.range(at: 1), in: responseString)!
                                       let idString = String(responseString[idRange])
                                       if !idString.isEmpty {
                                           groupId = idString
                                           print("📦 Found group ID in page content: \(idString)")
                                           break
                                       }
                                   }
                               }
                           } catch {
                               print("❌ Error searching for group ID in page: \(error)")
                           }
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
