import Foundation
import Security

class UserManager {
    static let shared = UserManager()
    
    private let userDefaults = UserDefaults.standard
    private let cookieKey = "user_cookie"
    private let usernameKey = "user_username"
    private let userIdKey = "user_id"
    private let isAdminKey = "user_is_admin"
    
    // Keychain keys for secure password storage
    private let passwordService = "GSaleApp"
    private let passwordAccount = "user_password"
    
    private init() {}
    
    // MARK: - Login Data
    var cookie: String? {
        get {
            let cookieValue = userDefaults.string(forKey: cookieKey)
            print("🍪 Retrieved cookie from UserDefaults: \(cookieValue ?? "nil")")
            return cookieValue
        }
        set {
            if let newValue = newValue {
                userDefaults.set(newValue, forKey: cookieKey)
                print("🍪 Cookie saved to UserDefaults")
            } else {
                userDefaults.removeObject(forKey: cookieKey)
                print("🗑️ Cookie removed from UserDefaults")
            }
        }
    }
    
    var username: String? {
        get {
            return userDefaults.string(forKey: usernameKey)
        }
        set {
            if let newValue = newValue {
                userDefaults.set(newValue, forKey: usernameKey)
                print("👤 Username saved: \(newValue)")
            } else {
                userDefaults.removeObject(forKey: usernameKey)
                print("🗑️ Username removed")
            }
        }
    }
    
    var userId: Int? {
        get {
            let value = userDefaults.integer(forKey: userIdKey)
            return value == 0 ? nil : value
        }
        set {
            if let newValue = newValue {
                userDefaults.set(newValue, forKey: userIdKey)
            } else {
                userDefaults.removeObject(forKey: userIdKey)
            }
        }
    }
    
    var isAdmin: Bool {
        get {
            return userDefaults.bool(forKey: isAdminKey)
        }
        set {
            userDefaults.set(newValue, forKey: isAdminKey)
        }
    }
    
    // MARK: - Password Management (Keychain)
    
    func savePassword(_ password: String) -> Bool {
        let passwordData = Data(password.utf8)
        
        // Create query for keychain
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: passwordService,
            kSecAttrAccount as String: passwordAccount,
            kSecValueData as String: passwordData
        ]
        
        // Delete existing item first
        SecItemDelete(query as CFDictionary)
        
        // Add new item
        let status = SecItemAdd(query as CFDictionary, nil)
        
        if status == errSecSuccess {
            print("🔐 Password saved securely to Keychain")
            return true
        } else {
            print("❌ Failed to save password to Keychain: \(status)")
            return false
        }
    }
    
    func getPassword() -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: passwordService,
            kSecAttrAccount as String: passwordAccount,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        
        if status == errSecSuccess {
            if let passwordData = result as? Data,
               let password = String(data: passwordData, encoding: .utf8) {
                print("🔐 Password retrieved from Keychain")
                return password
            }
        } else if status == errSecItemNotFound {
            print("📝 No saved password found in Keychain")
        } else {
            print("❌ Failed to retrieve password from Keychain: \(status)")
        }
        
        return nil
    }
    
    func deletePassword() -> Bool {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: passwordService,
            kSecAttrAccount as String: passwordAccount
        ]
        
        let status = SecItemDelete(query as CFDictionary)
        
        if status == errSecSuccess {
            print("🗑️ Password deleted from Keychain")
            return true
        } else if status == errSecItemNotFound {
            print("📝 No password to delete in Keychain")
            return true // Consider this success
        } else {
            print("❌ Failed to delete password from Keychain: \(status)")
            return false
        }
    }
    
    // MARK: - Convenience Methods
    
    func saveLoginData(cookie: String, username: String, userId: Int?, isAdmin: Bool, password: String? = nil) {
        self.cookie = cookie
        self.username = username
        self.userId = userId
        self.isAdmin = isAdmin
        
        if let password = password {
            _ = savePassword(password)
        }
        
        print("💾 Saved login data:")
        print("   Cookie: \(cookie)")
        print("   Username: \(username)")
        print("   User ID: \(userId ?? 0)")
        print("   Is Admin: \(isAdmin)")
        print("   Password saved: \(password != nil)")
    }
    
    func hasStoredCredentials() -> Bool {
        return username != nil && getPassword() != nil
    }
    
    func getStoredCredentials() -> (username: String, password: String)? {
        guard let username = self.username,
              let password = getPassword() else {
            return nil
        }
        return (username: username, password: password)
    }
    
    func clearAllData() {
        cookie = nil
        username = nil
        userId = nil
        isAdmin = false
        _ = deletePassword()
        
        print("🗑️ All user data cleared")
    }
    
    func isLoggedIn() -> Bool {
        return cookie != nil
    }
} 