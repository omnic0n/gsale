import Foundation

// MARK: - API Response Models
struct LoginResponse: Codable {
    let success: Bool
    let message: String
    var cookie: String?
    let user_id: Int?
    let username: String?
    let is_admin: Bool?
}

struct Group: Codable {
    let id: String
    let name: String
    let description: String?
    let created_at: String
    let updated_at: String
}

struct AddGroupResponse: Codable {
    let success: Bool
    let message: String
    let group_id: String?
}

struct GroupsResponse: Codable {
    let success: Bool
    let groups: [Group]
}

// MARK: - Group Detail Models
struct GroupDetail: Codable {
    let id: String
    let name: String
    let date: String
    let price: Double
    let totalItems: Int
    let totalSoldItems: Int
    let soldPrice: Double
    let items: [GroupItem]
    let imageFilename: String?
    
    // Location fields
    let latitude: Double?
    let longitude: Double?
    let locationAddress: String?
}

// MARK: - Location Model
struct Location {
    let latitude: Double
    let longitude: Double
    let address: String?
    
    var isValid: Bool {
        return latitude != 0 && longitude != 0
    }
}

struct GroupItem: Codable {
    let id: String
    let name: String
    let price: Double
    let sold: Bool
    let category: String?
    let storage: String?
}

struct ItemDetail: Codable {
    let id: String
    let name: String
    let sold: Bool
    let groupId: String
    let categoryId: String  // Changed from Int to String for UUID
    let category: String
    let returned: Bool
    let storage: String?
    let listDate: String?
    let groupName: String
    let purchaseDate: String
    let price: Double  // List price
    
    // Sold item financial details (only when sold = true)
    let soldPrice: Double?
    let shippingFee: Double?
    let netPrice: Double?
    let soldDate: String?
    let daysToSell: Int?
}

// MARK: - Category Model
struct Category: Codable {
    let id: String  // UUID
    let name: String
    let userId: String?
}

// MARK: - API Response
struct APIResponse<T: Codable>: Codable {
    let success: Bool
    let message: String
    let data: T?
} 

// MARK: - Reports Models
enum ReportInterval: String, Codable {
    case date
    case month
    case year
    case day
}

struct SalesReportRow: Codable {
    let date: String
    let day: String
    let soldPrice: Double
    let shippingFee: Double
    let net: Double
    let totalItems: Int
}

struct PurchasesReportRow: Codable {
    let date: String
    let day: String
    let price: Double
}

struct ProfitReportRow: Codable {
    let date: String
    let day: String
    let purchasePrice: Double
    let profit: Double
    let roiPercent: Double?
}

// MARK: - City Reports Models
struct CityOption: Codable {
    let name: String      // pure city key used for POST
    let label: String     // display label (e.g., "City (N purchases, $X)")
}

struct CityPurchaseRow: Codable {
    let id: String
    let name: String
    let date: String
    let purchasePrice: Double
    let locationName: String?
    let locationAddress: String?
    let latitude: Double?
    let longitude: Double?
    let itemCount: Int
    let soldCount: Int
    let totalSales: Double
    let profit: Double
}

struct CitySummary: Codable {
    let totalPurchases: Int
    let totalSpent: Double
    let totalItems: Int
    let soldItems: Int
    let totalSales: Double
    let totalProfit: Double
    let firstPurchase: String?
    let lastPurchase: String?
}