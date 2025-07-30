import Foundation

class UserManager {
    static let shared = UserManager()
    
    private let defaults = UserDefaults.standard
    private let cookieKey = "gsale_cookie"
    private let userIdKey = "gsale_user_id"
    private let usernameKey = "gsale_username"
    private let isAdminKey = "gsale_is_admin"
    
    private init() {}
    
    var isLoggedIn: Bool {
        return cookie != nil
    }
    
    var cookie: String? {
        get { defaults.string(forKey: cookieKey) }
        set { defaults.set(newValue, forKey: cookieKey) }
    }
    
    var userId: Int? {
        get { defaults.object(forKey: userIdKey) as? Int }
        set { defaults.set(newValue, forKey: userIdKey) }
    }
    
    var username: String? {
        get { defaults.string(forKey: usernameKey) }
        set { defaults.set(newValue, forKey: usernameKey) }
    }
    
    var isAdmin: Bool {
        get { defaults.bool(forKey: isAdminKey) }
        set { defaults.set(newValue, forKey: isAdminKey) }
    }
    
    func saveLoginData(from response: LoginResponse) {
        cookie = response.cookie
        userId = response.user_id
        username = response.username
        isAdmin = response.is_admin ?? false
    }
    
    func logout() {
        defaults.removeObject(forKey: cookieKey)
        defaults.removeObject(forKey: userIdKey)
        defaults.removeObject(forKey: usernameKey)
        defaults.removeObject(forKey: isAdminKey)
    }
} 