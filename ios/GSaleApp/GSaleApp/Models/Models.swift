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