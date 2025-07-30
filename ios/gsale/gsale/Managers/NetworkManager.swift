import Foundation

class NetworkManager {
    static let shared = NetworkManager()
    
    private let baseURL = "https://gsale.levimylesllc.com"
    private let session = URLSession.shared
    
    private init() {}
    
    // MARK: - Login
    func login(username: String, password: String, completion: @escaping (Result<LoginResponse, Error>) -> Void) {
        let url = URL(string: "\(baseURL)/login")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        
        let body = "username=\(username)&password=\(password)"
        request.httpBody = body.data(using: .utf8)
        
        session.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    completion(.failure(error))
                    return
                }
                
                guard let data = data else {
                    completion(.failure(NetworkError.noData))
                    return
                }
                
                do {
                    let response = try JSONDecoder().decode(LoginResponse.self, from: data)
                    completion(.success(response))
                } catch {
                    completion(.failure(error))
                }
            }
        }.resume()
    }
    
    // MARK: - Dashboard Data
    func getDashboardData(completion: @escaping (Result<DashboardData, Error>) -> Void) {
        let url = URL(string: "\(baseURL)/")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        // Add session cookie if available
        if let sessionCookie = UserManager.shared.getSessionCookie() {
            request.setValue(sessionCookie, forHTTPHeaderField: "Cookie")
        }
        
        session.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    completion(.failure(error))
                    return
                }
                
                guard let data = data else {
                    completion(.failure(NetworkError.noData))
                    return
                }
                
                do {
                    let dashboardData = try JSONDecoder().decode(DashboardData.self, from: data)
                    completion(.success(dashboardData))
                } catch {
                    completion(.failure(error))
                }
            }
        }.resume()
    }
    
    // MARK: - Items
    func getItems(completion: @escaping (Result<[Item], Error>) -> Void) {
        let url = URL(string: "\(baseURL)/items/list")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        if let sessionCookie = UserManager.shared.getSessionCookie() {
            request.setValue(sessionCookie, forHTTPHeaderField: "Cookie")
        }
        
        session.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    completion(.failure(error))
                    return
                }
                
                guard let data = data else {
                    completion(.failure(NetworkError.noData))
                    return
                }
                
                do {
                    let items = try JSONDecoder().decode([Item].self, from: data)
                    completion(.success(items))
                } catch {
                    completion(.failure(error))
                }
            }
        }.resume()
    }
    
    // MARK: - Groups
    func getGroups(completion: @escaping (Result<[Group], Error>) -> Void) {
        let url = URL(string: "\(baseURL)/groups/list")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        if let sessionCookie = UserManager.shared.getSessionCookie() {
            request.setValue(sessionCookie, forHTTPHeaderField: "Cookie")
        }
        
        session.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    completion(.failure(error))
                    return
                }
                
                guard let data = data else {
                    completion(.failure(NetworkError.noData))
                    return
                }
                
                do {
                    let groups = try JSONDecoder().decode([Group].self, from: data)
                    completion(.success(groups))
                } catch {
                    completion(.failure(error))
                }
            }
        }.resume()
    }
    
    // MARK: - Expenses
    func getExpenses(completion: @escaping (Result<[Expense], Error>) -> Void) {
        let url = URL(string: "\(baseURL)/expense/list")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        if let sessionCookie = UserManager.shared.getSessionCookie() {
            request.setValue(sessionCookie, forHTTPHeaderField: "Cookie")
        }
        
        session.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    completion(.failure(error))
                    return
                }
                
                guard let data = data else {
                    completion(.failure(NetworkError.noData))
                    return
                }
                
                do {
                    let expenses = try JSONDecoder().decode([Expense].self, from: data)
                    completion(.success(expenses))
                } catch {
                    completion(.failure(error))
                }
            }
        }.resume()
    }
    
    // MARK: - Reports
    func getReports(completion: @escaping (Result<ReportsData, Error>) -> Void) {
        let url = URL(string: "\(baseURL)/reports/profit")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        if let sessionCookie = UserManager.shared.getSessionCookie() {
            request.setValue(sessionCookie, forHTTPHeaderField: "Cookie")
        }
        
        session.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    completion(.failure(error))
                    return
                }
                
                guard let data = data else {
                    completion(.failure(NetworkError.noData))
                    return
                }
                
                do {
                    let reportsData = try JSONDecoder().decode(ReportsData.self, from: data)
                    completion(.success(reportsData))
                } catch {
                    completion(.failure(error))
                }
            }
        }.resume()
    }
    
    // MARK: - Admin
    func getUsers(completion: @escaping (Result<[User], Error>) -> Void) {
        let url = URL(string: "\(baseURL)/admin")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        if let sessionCookie = UserManager.shared.getSessionCookie() {
            request.setValue(sessionCookie, forHTTPHeaderField: "Cookie")
        }
        
        session.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    completion(.failure(error))
                    return
                }
                
                guard let data = data else {
                    completion(.failure(NetworkError.noData))
                    return
                }
                
                do {
                    let users = try JSONDecoder().decode([User].self, from: data)
                    completion(.success(users))
                } catch {
                    completion(.failure(error))
                }
            }
        }.resume()
    }
}

// MARK: - Error Types
enum NetworkError: Error {
    case noData
    case invalidResponse
    case unauthorized
    case serverError
}

// MARK: - Response Models
struct LoginResponse: Codable {
    let success: Bool
    let message: String
    let user: User?
}

struct DashboardData: Codable {
    let items: [Item]
    let totalProfit: Double
    let totalSales: Int
    let totalPurchases: Int
}

struct Item: Codable {
    let id: String
    let name: String
    let description: String?
    let purchasePrice: Double
    let salePrice: Double?
    let sold: Bool
    let groupId: String?
    let createdAt: String
}

struct Group: Codable {
    let id: String
    let name: String
    let description: String?
    let itemCount: Int
    let totalValue: Double
}

struct Expense: Codable {
    let id: String
    let name: String
    let amount: Double
    let type: String
    let date: String
    let description: String?
}

struct ReportsData: Codable {
    let profitData: [ProfitData]
    let salesData: [SalesData]
    let expenseData: [ExpenseData]
}

struct ProfitData: Codable {
    let year: String
    let profit: Double
    let sales: Int
    let purchases: Int
}

struct SalesData: Codable {
    let date: String
    let amount: Double
    let itemCount: Int
}

struct ExpenseData: Codable {
    let category: String
    let amount: Double
    let count: Int
}

struct User: Codable {
    let id: String
    let username: String
    let email: String
    let isAdmin: Bool
    let createdAt: String
} 