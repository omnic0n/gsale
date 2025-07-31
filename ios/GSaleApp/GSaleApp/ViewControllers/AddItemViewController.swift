import UIKit

class AddItemViewController: UIViewController {
    
    // UI Elements
    private let scrollView = UIScrollView()
    private let contentView = UIView()
    private let headerLabel = UILabel()
    
    private let nameLabel = UILabel()
    private let nameTextField = UITextField()
    
    private let categoryLabel = UILabel()
    private let categoryButton = UIButton(type: .system)
    private var selectedCategoryId: String?
    private var categories: [Category] = []
    
    private let storageLabel = UILabel()
    private let storageTextField = UITextField()
    
    private let listDateLabel = UILabel()
    private let listDatePicker = UIDatePicker()
    
    private let addButton = UIButton(type: .system)
    private let cancelButton = UIButton(type: .system)
    
    private let activityIndicator = UIActivityIndicatorView(style: .large)
    
    // Properties
    private let groupId: String
    private let groupName: String
    
    // MARK: - Initialization
    
    init(groupId: String, groupName: String) {
        self.groupId = groupId
        self.groupName = groupName
        super.init(nibName: nil, bundle: nil)
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    // MARK: - Lifecycle
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupConstraints()
        loadCategories()
    }
    
    // MARK: - UI Setup
    
    private func setupUI() {
        view.backgroundColor = .systemGroupedBackground
        title = "Add Item"
        
        // Navigation items
        navigationItem.leftBarButtonItem = UIBarButtonItem(
            title: "Cancel",
            style: .plain,
            target: self,
            action: #selector(cancelTapped)
        )
        
        // Scroll view
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        scrollView.showsVerticalScrollIndicator = true
        view.addSubview(scrollView)
        
        // Content view
        contentView.translatesAutoresizingMaskIntoConstraints = false
        scrollView.addSubview(contentView)
        
        // Header
        headerLabel.text = "Add Item to \"\(groupName)\""
        headerLabel.font = UIFont.boldSystemFont(ofSize: 20)
        headerLabel.textAlignment = .center
        headerLabel.textColor = .label
        headerLabel.numberOfLines = 0
        headerLabel.translatesAutoresizingMaskIntoConstraints = false
        contentView.addSubview(headerLabel)
        
        // Item Name
        nameLabel.text = "Item Name"
        nameLabel.font = UIFont.systemFont(ofSize: 16, weight: .medium)
        nameLabel.textColor = .label
        nameLabel.translatesAutoresizingMaskIntoConstraints = false
        contentView.addSubview(nameLabel)
        
        nameTextField.borderStyle = .roundedRect
        nameTextField.placeholder = "Enter item name"
        nameTextField.font = UIFont.systemFont(ofSize: 16)
        nameTextField.translatesAutoresizingMaskIntoConstraints = false
        contentView.addSubview(nameTextField)
        
        // Category
        categoryLabel.text = "Category"
        categoryLabel.font = UIFont.systemFont(ofSize: 16, weight: .medium)
        categoryLabel.textColor = .label
        categoryLabel.translatesAutoresizingMaskIntoConstraints = false
        contentView.addSubview(categoryLabel)
        
        categoryButton.setTitle("Select Category", for: .normal)
        categoryButton.titleLabel?.font = UIFont.systemFont(ofSize: 16)
        categoryButton.backgroundColor = .systemGray6
        categoryButton.layer.cornerRadius = 8
        categoryButton.contentHorizontalAlignment = .left
        if #available(iOS 15.0, *) {
            var config = UIButton.Configuration.plain()
            config.contentInsets = NSDirectionalEdgeInsets(top: 12, leading: 16, bottom: 12, trailing: 16)
            categoryButton.configuration = config
        } else {
            categoryButton.contentEdgeInsets = UIEdgeInsets(top: 12, left: 16, bottom: 12, right: 16)
        }
        categoryButton.addTarget(self, action: #selector(categoryButtonTapped), for: .touchUpInside)
        categoryButton.translatesAutoresizingMaskIntoConstraints = false
        contentView.addSubview(categoryButton)
        
        // Storage
        storageLabel.text = "Storage Location"
        storageLabel.font = UIFont.systemFont(ofSize: 16, weight: .medium)
        storageLabel.textColor = .label
        storageLabel.translatesAutoresizingMaskIntoConstraints = false
        contentView.addSubview(storageLabel)
        
        storageTextField.borderStyle = .roundedRect
        storageTextField.placeholder = "Enter storage location (optional)"
        storageTextField.font = UIFont.systemFont(ofSize: 16)
        storageTextField.translatesAutoresizingMaskIntoConstraints = false
        contentView.addSubview(storageTextField)
        
        // List Date
        listDateLabel.text = "List Date"
        listDateLabel.font = UIFont.systemFont(ofSize: 16, weight: .medium)
        listDateLabel.textColor = .label
        listDateLabel.translatesAutoresizingMaskIntoConstraints = false
        contentView.addSubview(listDateLabel)
        
        listDatePicker.datePickerMode = .date
        listDatePicker.preferredDatePickerStyle = .compact
        listDatePicker.date = Date()
        listDatePicker.translatesAutoresizingMaskIntoConstraints = false
        contentView.addSubview(listDatePicker)
        
        // Add Button
        addButton.setTitle("🔹 Add Item", for: .normal)
        addButton.titleLabel?.font = UIFont.boldSystemFont(ofSize: 18)
        addButton.backgroundColor = .systemBlue
        addButton.setTitleColor(.white, for: .normal)
        addButton.layer.cornerRadius = 12
        addButton.layer.shadowColor = UIColor.black.cgColor
        addButton.layer.shadowOffset = CGSize(width: 0, height: 2)
        addButton.layer.shadowOpacity = 0.1
        addButton.layer.shadowRadius = 4
        addButton.addTarget(self, action: #selector(addItemTapped), for: .touchUpInside)
        addButton.translatesAutoresizingMaskIntoConstraints = false
        contentView.addSubview(addButton)
        
        // Cancel Button
        cancelButton.setTitle("Cancel", for: .normal)
        cancelButton.titleLabel?.font = UIFont.systemFont(ofSize: 16)
        cancelButton.setTitleColor(.systemRed, for: .normal)
        cancelButton.addTarget(self, action: #selector(cancelTapped), for: .touchUpInside)
        cancelButton.translatesAutoresizingMaskIntoConstraints = false
        contentView.addSubview(cancelButton)
        
        // Activity Indicator
        activityIndicator.translatesAutoresizingMaskIntoConstraints = false
        activityIndicator.hidesWhenStopped = true
        view.addSubview(activityIndicator)
        
        // Add button press animation
        addButton.addTarget(self, action: #selector(addButtonPressed), for: .touchDown)
        addButton.addTarget(self, action: #selector(addButtonReleased), for: [.touchUpInside, .touchUpOutside, .touchCancel])
    }
    
    private func setupConstraints() {
        NSLayoutConstraint.activate([
            // Scroll View
            scrollView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            
            // Content View
            contentView.topAnchor.constraint(equalTo: scrollView.topAnchor),
            contentView.leadingAnchor.constraint(equalTo: scrollView.leadingAnchor),
            contentView.trailingAnchor.constraint(equalTo: scrollView.trailingAnchor),
            contentView.bottomAnchor.constraint(equalTo: scrollView.bottomAnchor),
            contentView.widthAnchor.constraint(equalTo: scrollView.widthAnchor),
            
            // Header
            headerLabel.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 20),
            headerLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            headerLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            // Item Name
            nameLabel.topAnchor.constraint(equalTo: headerLabel.bottomAnchor, constant: 30),
            nameLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            nameLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            nameTextField.topAnchor.constraint(equalTo: nameLabel.bottomAnchor, constant: 8),
            nameTextField.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            nameTextField.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            nameTextField.heightAnchor.constraint(equalToConstant: 44),
            
            // Category
            categoryLabel.topAnchor.constraint(equalTo: nameTextField.bottomAnchor, constant: 20),
            categoryLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            categoryLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            categoryButton.topAnchor.constraint(equalTo: categoryLabel.bottomAnchor, constant: 8),
            categoryButton.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            categoryButton.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            categoryButton.heightAnchor.constraint(equalToConstant: 44),
            
            // Storage
            storageLabel.topAnchor.constraint(equalTo: categoryButton.bottomAnchor, constant: 20),
            storageLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            storageLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            storageTextField.topAnchor.constraint(equalTo: storageLabel.bottomAnchor, constant: 8),
            storageTextField.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            storageTextField.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            storageTextField.heightAnchor.constraint(equalToConstant: 44),
            
            // List Date
            listDateLabel.topAnchor.constraint(equalTo: storageTextField.bottomAnchor, constant: 20),
            listDateLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            listDateLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            listDatePicker.topAnchor.constraint(equalTo: listDateLabel.bottomAnchor, constant: 8),
            listDatePicker.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            listDatePicker.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            // Add Button
            addButton.topAnchor.constraint(equalTo: listDatePicker.bottomAnchor, constant: 40),
            addButton.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            addButton.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            addButton.heightAnchor.constraint(equalToConstant: 50),
            
            // Cancel Button
            cancelButton.topAnchor.constraint(equalTo: addButton.bottomAnchor, constant: 16),
            cancelButton.centerXAnchor.constraint(equalTo: contentView.centerXAnchor),
            cancelButton.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -20),
            cancelButton.heightAnchor.constraint(equalToConstant: 44),
            
            // Activity Indicator
            activityIndicator.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            activityIndicator.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }
    
    // MARK: - Actions
    
    @objc private func categoryButtonTapped() {
        guard !categories.isEmpty else {
            showAlert(title: "Loading", message: "Categories are still loading. Please try again in a moment.")
            return
        }
        
        let alertController = UIAlertController(title: "Select Category", message: nil, preferredStyle: .actionSheet)
        
        for category in categories {
            let action = UIAlertAction(title: category.name, style: .default) { _ in
                self.selectedCategoryId = category.id
                self.categoryButton.setTitle(category.name, for: .normal)
            }
            alertController.addAction(action)
        }
        
        let cancelAction = UIAlertAction(title: "Cancel", style: .cancel)
        alertController.addAction(cancelAction)
        
        // For iPad
        if let popover = alertController.popoverPresentationController {
            popover.sourceView = categoryButton
            popover.sourceRect = categoryButton.bounds
        }
        
        present(alertController, animated: true)
    }
    
    @objc private func addItemTapped() {
        // Validate required fields
        guard let itemName = nameTextField.text, !itemName.isEmpty else {
            showAlert(title: "Validation Error", message: "Please enter an item name.")
            return
        }
        
        guard let categoryId = selectedCategoryId else {
            showAlert(title: "Validation Error", message: "Please select a category.")
            return
        }
        
        let storage = storageTextField.text ?? ""
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        let listDate = formatter.string(from: listDatePicker.date)
        
        // Show loading
        activityIndicator.startAnimating()
        addButton.isEnabled = false
        
        Task {
            do {
                let success = try await NetworkManager.shared.addItem(
                    itemName: itemName,
                    groupId: groupId,
                    categoryId: categoryId,
                    storage: storage,
                    listDate: listDate
                )
                
                await MainActor.run {
                    activityIndicator.stopAnimating()
                    addButton.isEnabled = true
                    
                    if success {
                        // Post notification to refresh group details
                        NotificationCenter.default.post(name: .itemAdded, object: nil)
                        showSuccessAndDismiss()
                    } else {
                        showAlert(title: "Error", message: "Failed to add item. Please try again.")
                    }
                }
            } catch {
                await MainActor.run {
                    activityIndicator.stopAnimating()
                    addButton.isEnabled = true
                    
                    if let networkError = error as? NetworkError {
                        switch networkError {
                        case .unauthorized:
                            showAlert(title: "Authentication Error", message: "Please log in again.")
                        case .serverError(let message):
                            showAlert(title: "Server Error", message: message)
                        case .invalidResponse:
                            showAlert(title: "Error", message: "Invalid response from server.")
                        case .invalidURL:
                            showAlert(title: "Error", message: "Invalid URL.")
                        case .noData:
                            showAlert(title: "Error", message: "No data received from server.")
                        case .decodingError:
                            showAlert(title: "Error", message: "Failed to decode response.")
                        }
                    } else {
                        showAlert(title: "Error", message: "Failed to add item: \(error.localizedDescription)")
                    }
                }
            }
        }
    }
    
    @objc private func cancelTapped() {
        dismiss(animated: true)
    }
    
    // MARK: - Button Animation
    
    @objc private func addButtonPressed() {
        UIView.animate(withDuration: 0.1) {
            self.addButton.transform = CGAffineTransform(scaleX: 0.95, y: 0.95)
        }
    }
    
    @objc private func addButtonReleased() {
        UIView.animate(withDuration: 0.1) {
            self.addButton.transform = CGAffineTransform.identity
        }
    }
    
    // MARK: - Helper Methods
    
    private func loadCategories() {
        Task {
            do {
                let loadedCategories = try await NetworkManager.shared.getCategories()
                await MainActor.run {
                    self.categories = loadedCategories
                    print("📋 Loaded \(loadedCategories.count) categories")
                }
            } catch {
                await MainActor.run {
                    print("❌ Failed to load categories: \(error)")
                    self.showAlert(title: "Error", message: "Failed to load categories. Please try again.")
                }
            }
        }
    }
    
    private func showSuccessAndDismiss() {
        let alert = UIAlertController(title: "Success", message: "Item added successfully!", preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default) { _ in
            self.dismiss(animated: true)
        })
        present(alert, animated: true)
    }
    
    private func showAlert(title: String, message: String) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
}

// MARK: - Extensions

extension Notification.Name {
    static let itemAdded = Notification.Name("itemAdded")
}

 