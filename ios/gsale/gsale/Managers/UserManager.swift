import Foundation

class UserManager {
    static let shared = UserManager()
    
    private let userDefaults = UserDefaults.standard
    private let sessionCookieKey = "sessionCookie"
    private let userIdKey = "userId"
    private let usernameKey = "username"
    private let isAdminKey = "isAdmin"
    
    private init() {}
    
    // MARK: - Session Management
    func saveSessionCookie(_ cookie: String) {
        userDefaults.set(cookie, forKey: sessionCookieKey)
    }
    
    func getSessionCookie() -> String? {
        return userDefaults.string(forKey: sessionCookieKey)
    }
    
    func clearSessionCookie() {
        userDefaults.removeObject(forKey: sessionCookieKey)
    }
    
    // MARK: - User Data
    func saveUserData(userId: String, username: String, isAdmin: Bool) {
        userDefaults.set(userId, forKey: userIdKey)
        userDefaults.set(username, forKey: usernameKey)
        userDefaults.set(isAdmin, forKey: isAdminKey)
    }
    
    func getUserId() -> String? {
        return userDefaults.string(forKey: userIdKey)
    }
    
    func getUsername() -> String? {
        return userDefaults.string(forKey: usernameKey)
    }
    
    func isAdmin() -> Bool {
        return userDefaults.bool(forKey: isAdminKey)
    }
    
    func clearUserData() {
        userDefaults.removeObject(forKey: userIdKey)
        userDefaults.removeObject(forKey: usernameKey)
        userDefaults.removeObject(forKey: isAdminKey)
    }
    
    // MARK: - Login State
    func isLoggedIn() -> Bool {
        return getSessionCookie() != nil && getUserId() != nil
    }
    
    func logout() {
        clearSessionCookie()
        clearUserData()
    }
} 