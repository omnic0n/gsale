import UIKit

class GroupDetailViewController: UIViewController {
    
    private let scrollView = UIScrollView()
    private let contentView = UIView()
    
    private let headerView = UIView()
    private let nameLabel = UILabel()
    private let dateLabel = UILabel()
    private let priceLabel = UILabel()
    private let statsView = UIView()
    private let totalItemsLabel = UILabel()
    private let soldItemsLabel = UILabel()
    private let soldPriceLabel = UILabel()
    private let profitLabel = UILabel()
    
    private let modifyButton = UIButton(type: .system)
    private let addItemButton = UIButton(type: .system)
    private let deleteButton = UIButton(type: .system)
    private let locationButton = UIButton(type: .system)
    
    private let itemsTableView = UITableView()
    private let itemsLabel = UILabel()
    
    private let groupImageView = UIImageView()
    private let imageActivityIndicator = UIActivityIndicatorView(style: .medium)
    
    // Constraint that changes based on image presence
    private var statsViewTopConstraint: NSLayoutConstraint!
    
    private var groupDetail: GroupDetail
    
    init(groupDetail: GroupDetail) {
        self.groupDetail = groupDetail
        super.init(nibName: nil, bundle: nil)
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupData()
        setupHomeButton()
        
        // Add notification observer for item additions
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(itemWasAdded),
            name: .itemAdded,
            object: nil
        )
        // Refresh on group updates
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(groupWasUpdated(_:)),
            name: .groupUpdated,
            object: nil
        )
    }
    
    deinit {
        NotificationCenter.default.removeObserver(self)
    }
    
    private func setupUI() {
        view.backgroundColor = .systemGroupedBackground
        title = "Group Details"
        
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        contentView.translatesAutoresizingMaskIntoConstraints = false
        
        view.addSubview(scrollView)
        scrollView.addSubview(contentView)
        
        // Header setup - Enhanced styling
        headerView.backgroundColor = .systemBackground
        headerView.layer.cornerRadius = 16
        headerView.layer.shadowColor = UIColor.black.cgColor
        headerView.layer.shadowOffset = CGSize(width: 0, height: 2)
        headerView.layer.shadowOpacity = 0.1
        headerView.layer.shadowRadius = 8
        headerView.translatesAutoresizingMaskIntoConstraints = false
        
        nameLabel.font = UIFont.systemFont(ofSize: 28, weight: .bold)
        nameLabel.textColor = .label
        nameLabel.textAlignment = .center
        nameLabel.numberOfLines = 0
        nameLabel.translatesAutoresizingMaskIntoConstraints = false
        
        dateLabel.font = UIFont.systemFont(ofSize: 16, weight: .medium)
        dateLabel.textColor = .systemGray
        dateLabel.textAlignment = .center
        dateLabel.translatesAutoresizingMaskIntoConstraints = false
        
        priceLabel.font = UIFont.systemFont(ofSize: 24, weight: .bold)
        priceLabel.textColor = .systemGreen
        priceLabel.textAlignment = .center
        priceLabel.translatesAutoresizingMaskIntoConstraints = false
        
        // Stats setup - Enhanced styling
        statsView.backgroundColor = .secondarySystemBackground
        statsView.layer.cornerRadius = 12
        statsView.layer.borderWidth = 1
        statsView.layer.borderColor = UIColor.systemGray5.cgColor
        statsView.translatesAutoresizingMaskIntoConstraints = false
        
        totalItemsLabel.font = UIFont.systemFont(ofSize: 17, weight: .semibold)
        totalItemsLabel.textColor = .systemBlue
        totalItemsLabel.textAlignment = .center
        totalItemsLabel.numberOfLines = 0
        totalItemsLabel.translatesAutoresizingMaskIntoConstraints = false
        
        soldItemsLabel.font = UIFont.systemFont(ofSize: 17, weight: .semibold)
        soldItemsLabel.textColor = .systemOrange
        soldItemsLabel.textAlignment = .center
        soldItemsLabel.numberOfLines = 0
        soldItemsLabel.translatesAutoresizingMaskIntoConstraints = false
        
        soldPriceLabel.font = UIFont.systemFont(ofSize: 17, weight: .semibold)
        soldPriceLabel.textColor = .systemGreen
        soldPriceLabel.textAlignment = .center
        soldPriceLabel.numberOfLines = 0
        soldPriceLabel.translatesAutoresizingMaskIntoConstraints = false
        
        profitLabel.font = UIFont.systemFont(ofSize: 17, weight: .semibold)
        profitLabel.textColor = .systemGreen
        profitLabel.textAlignment = .center
        profitLabel.numberOfLines = 0
        profitLabel.translatesAutoresizingMaskIntoConstraints = false
        
        // Enhanced button styling
        setupButton(modifyButton, title: "✏️ Modify Group", backgroundColor: .systemBlue)
        modifyButton.addTarget(self, action: #selector(modifyButtonTapped), for: .touchUpInside)
        
        setupButton(addItemButton, title: "➕ Add Item", backgroundColor: .systemGreen)
        addItemButton.addTarget(self, action: #selector(addItemButtonTapped), for: .touchUpInside)
        
        setupButton(deleteButton, title: "🗑️ Delete Group", backgroundColor: .systemRed)
        deleteButton.addTarget(self, action: #selector(deleteButtonTapped), for: .touchUpInside)
        
        // Setup location button - only show if location data exists
        if let locationAddress = groupDetail.locationAddress, !locationAddress.isEmpty {
            setupButton(locationButton, title: "📍 \(locationAddress)", backgroundColor: .systemPurple)
            locationButton.addTarget(self, action: #selector(locationButtonTapped), for: .touchUpInside)
            locationButton.titleLabel?.numberOfLines = 0
            locationButton.titleLabel?.textAlignment = .center
        } else if let latitude = groupDetail.latitude, let longitude = groupDetail.longitude, 
                  latitude != 0, longitude != 0 {
            let coordinates = String(format: "📍 %.6f, %.6f", latitude, longitude)
            setupButton(locationButton, title: coordinates, backgroundColor: .systemPurple)
            locationButton.addTarget(self, action: #selector(locationButtonTapped), for: .touchUpInside)
            locationButton.titleLabel?.numberOfLines = 0
            locationButton.titleLabel?.textAlignment = .center
        }
        
        // Items setup - Enhanced styling
        itemsLabel.text = "📦 Items (\(groupDetail.items.count))"
        itemsLabel.font = UIFont.systemFont(ofSize: 22, weight: .bold)
        itemsLabel.textColor = .label
        itemsLabel.textAlignment = .center
        itemsLabel.translatesAutoresizingMaskIntoConstraints = false
        
        itemsTableView.delegate = self
        itemsTableView.dataSource = self
        itemsTableView.register(UITableViewCell.self, forCellReuseIdentifier: "ItemCell")
        itemsTableView.translatesAutoresizingMaskIntoConstraints = false
        itemsTableView.isScrollEnabled = false
        itemsTableView.separatorStyle = .singleLine
        itemsTableView.separatorInset = UIEdgeInsets(top: 0, left: 20, bottom: 0, right: 20)
        itemsTableView.separatorColor = .systemGray4
        itemsTableView.layer.cornerRadius = 12
        itemsTableView.backgroundColor = .systemBackground
        itemsTableView.layer.borderWidth = 1
        itemsTableView.layer.borderColor = UIColor.systemGray5.cgColor
        itemsTableView.rowHeight = 50
        itemsTableView.tableFooterView = UIView() // Remove extra separators
        
        // Add subviews
        headerView.addSubview(nameLabel)
        headerView.addSubview(dateLabel)
        headerView.addSubview(priceLabel)
        headerView.addSubview(groupImageView)
        headerView.addSubview(imageActivityIndicator)
        headerView.addSubview(statsView)
        
        statsView.addSubview(totalItemsLabel)
        statsView.addSubview(soldItemsLabel)
        statsView.addSubview(soldPriceLabel)
        statsView.addSubview(profitLabel)
        
        contentView.addSubview(headerView)
        contentView.addSubview(modifyButton)
        contentView.addSubview(addItemButton)
        contentView.addSubview(deleteButton)
        
        // Only add location button if there's location data
        if hasLocationData() {
            contentView.addSubview(locationButton)
        }
        
        contentView.addSubview(itemsLabel)
        contentView.addSubview(itemsTableView)
        
        // Setup image view
        groupImageView.translatesAutoresizingMaskIntoConstraints = false
        groupImageView.contentMode = .scaleAspectFill
        groupImageView.layer.cornerRadius = 8
        groupImageView.layer.masksToBounds = true
        groupImageView.backgroundColor = .systemGray6
        groupImageView.layer.borderWidth = 1
        groupImageView.layer.borderColor = UIColor.systemGray4.cgColor
        groupImageView.isHidden = true // Initially hidden until image loads
        
        // Setup image loading indicator
        imageActivityIndicator.translatesAutoresizingMaskIntoConstraints = false
        imageActivityIndicator.hidesWhenStopped = true
        
        setupConstraints()
    }

    private func setupHomeButton() {
        let homeImage = UIImage(systemName: "house.fill")
        let homeButton = UIBarButtonItem(image: homeImage, style: .plain, target: self, action: #selector(goHome))
        navigationItem.rightBarButtonItem = homeButton
    }

    @objc private func goHome() {
        navigationController?.popToRootViewController(animated: true)
    }
    
    private func setupButton(_ button: UIButton, title: String, backgroundColor: UIColor) {
        button.setTitle(title, for: .normal)
        button.backgroundColor = backgroundColor
        button.setTitleColor(.white, for: .normal)
        button.layer.cornerRadius = 12
        button.titleLabel?.font = UIFont.systemFont(ofSize: 17, weight: .semibold)
        button.translatesAutoresizingMaskIntoConstraints = false
        
        // Add subtle shadow
        button.layer.shadowColor = backgroundColor.cgColor
        button.layer.shadowOffset = CGSize(width: 0, height: 2)
        button.layer.shadowOpacity = 0.3
        button.layer.shadowRadius = 4
        
        // Add press animation
        button.addTarget(self, action: #selector(buttonPressed(_:)), for: .touchDown)
        button.addTarget(self, action: #selector(buttonReleased(_:)), for: [.touchUpInside, .touchUpOutside, .touchCancel])
    }
    
    @objc private func buttonPressed(_ sender: UIButton) {
        UIView.animate(withDuration: 0.1) {
            sender.transform = CGAffineTransform(scaleX: 0.95, y: 0.95)
        }
    }
    
    @objc private func buttonReleased(_ sender: UIButton) {
        UIView.animate(withDuration: 0.1) {
            sender.transform = CGAffineTransform.identity
        }
    }
    
    private func setupConstraints() {
        NSLayoutConstraint.activate([
            scrollView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            
            contentView.topAnchor.constraint(equalTo: scrollView.topAnchor),
            contentView.leadingAnchor.constraint(greaterThanOrEqualTo: scrollView.leadingAnchor),
            contentView.trailingAnchor.constraint(lessThanOrEqualTo: scrollView.trailingAnchor),
            contentView.bottomAnchor.constraint(equalTo: scrollView.bottomAnchor),
            contentView.centerXAnchor.constraint(equalTo: scrollView.centerXAnchor),
            contentView.widthAnchor.constraint(lessThanOrEqualToConstant: 400),
            contentView.widthAnchor.constraint(greaterThanOrEqualToConstant: 300),
            
            headerView.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 24),
            headerView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            headerView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            nameLabel.topAnchor.constraint(equalTo: headerView.topAnchor, constant: 24),
            nameLabel.leadingAnchor.constraint(equalTo: headerView.leadingAnchor, constant: 20),
            nameLabel.trailingAnchor.constraint(equalTo: headerView.trailingAnchor, constant: -20),
            
            dateLabel.topAnchor.constraint(equalTo: nameLabel.bottomAnchor, constant: 12),
            dateLabel.leadingAnchor.constraint(equalTo: headerView.leadingAnchor, constant: 20),
            dateLabel.trailingAnchor.constraint(equalTo: headerView.trailingAnchor, constant: -20),
            
            priceLabel.topAnchor.constraint(equalTo: dateLabel.bottomAnchor, constant: 16),
            priceLabel.leadingAnchor.constraint(equalTo: headerView.leadingAnchor, constant: 20),
            priceLabel.trailingAnchor.constraint(equalTo: headerView.trailingAnchor, constant: -20),
            
            // Image view constraints (under price label)
            groupImageView.topAnchor.constraint(equalTo: priceLabel.bottomAnchor, constant: 16),
            groupImageView.centerXAnchor.constraint(equalTo: headerView.centerXAnchor),
            groupImageView.widthAnchor.constraint(equalToConstant: 150),
            groupImageView.heightAnchor.constraint(equalToConstant: 150),
            
            // Image loading indicator constraints
            imageActivityIndicator.centerXAnchor.constraint(equalTo: groupImageView.centerXAnchor),
            imageActivityIndicator.centerYAnchor.constraint(equalTo: groupImageView.centerYAnchor),
            
            statsView.leadingAnchor.constraint(equalTo: headerView.leadingAnchor, constant: 16),
            statsView.trailingAnchor.constraint(equalTo: headerView.trailingAnchor, constant: -16),
            statsView.heightAnchor.constraint(equalToConstant: 160),
            
            totalItemsLabel.topAnchor.constraint(equalTo: statsView.topAnchor, constant: 16),
            totalItemsLabel.centerXAnchor.constraint(equalTo: statsView.centerXAnchor),
            
            soldItemsLabel.topAnchor.constraint(equalTo: totalItemsLabel.bottomAnchor, constant: 8),
            soldItemsLabel.centerXAnchor.constraint(equalTo: statsView.centerXAnchor),
            
            soldPriceLabel.topAnchor.constraint(equalTo: soldItemsLabel.bottomAnchor, constant: 8),
            soldPriceLabel.centerXAnchor.constraint(equalTo: statsView.centerXAnchor),
            
            profitLabel.topAnchor.constraint(equalTo: soldPriceLabel.bottomAnchor, constant: 8),
            profitLabel.centerXAnchor.constraint(equalTo: statsView.centerXAnchor),
            
            modifyButton.topAnchor.constraint(equalTo: statsView.bottomAnchor, constant: 24),
            modifyButton.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            modifyButton.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            modifyButton.heightAnchor.constraint(equalToConstant: 56),
            
            addItemButton.topAnchor.constraint(equalTo: modifyButton.bottomAnchor, constant: 16),
            addItemButton.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            addItemButton.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            addItemButton.heightAnchor.constraint(equalToConstant: 56),
            
            deleteButton.topAnchor.constraint(equalTo: addItemButton.bottomAnchor, constant: 16),
            deleteButton.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            deleteButton.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            deleteButton.heightAnchor.constraint(equalToConstant: 56),
        ])
        
        // Conditionally add location button constraints
        var itemsLabelTopAnchor: NSLayoutYAxisAnchor = deleteButton.bottomAnchor
        var itemsLabelTopConstant: CGFloat = 40
        
        if hasLocationData() {
            NSLayoutConstraint.activate([
                locationButton.topAnchor.constraint(equalTo: deleteButton.bottomAnchor, constant: 16),
                locationButton.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
                locationButton.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
                locationButton.heightAnchor.constraint(equalToConstant: 56),
            ])
            itemsLabelTopAnchor = locationButton.bottomAnchor
        }
        
        NSLayoutConstraint.activate([
            itemsLabel.topAnchor.constraint(equalTo: itemsLabelTopAnchor, constant: itemsLabelTopConstant),
            itemsLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            itemsLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            itemsTableView.topAnchor.constraint(equalTo: itemsLabel.bottomAnchor, constant: 20),
            itemsTableView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            itemsTableView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            itemsTableView.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -20),
            itemsTableView.heightAnchor.constraint(equalToConstant: CGFloat(max(groupDetail.items.count * 50, 50)))
        ])
        
        // Set up dynamic constraint for stats view position
        // Initially set to position after price (no image case)
        statsViewTopConstraint = statsView.topAnchor.constraint(equalTo: priceLabel.bottomAnchor, constant: 20)
        statsViewTopConstraint.isActive = true
    }
    
    private func setupData() {
        nameLabel.text = groupDetail.name
        dateLabel.text = "Date: \(groupDetail.date)"
        priceLabel.text = "Price: $\(String(format: "%.2f", groupDetail.price))"
        
        totalItemsLabel.text = "📦 Total Items: \(groupDetail.totalItems)"
        soldItemsLabel.text = "💰 Sold Items: \(groupDetail.totalSoldItems)"
        soldPriceLabel.text = "💵 Sold Price: $\(String(format: "%.2f", groupDetail.soldPrice))"
        
        // Compute profit as sold net minus purchase price
        let profit = groupDetail.soldPrice - groupDetail.price
        profitLabel.text = "📈 Profit: $\(String(format: "%.2f", profit))"
        profitLabel.textColor = profit < 0 ? .systemRed : .systemGreen
        
        // Check if we have items, if not load them immediately
        if !groupDetail.items.isEmpty {
            updateItemsDisplay(with: groupDetail.items)
        } else {
            loadActualItemsSimple()
        }
        
        // Load group image if available
        loadGroupImage()
        
        // Debug: Print button frame after layout
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
        }
    }
    
        @objc private func modifyButtonTapped() {
        // Navigate to modify group page
        let modifyGroupVC = ModifyGroupViewController(groupId: groupDetail.id, groupName: groupDetail.name)
        navigationController?.pushViewController(modifyGroupVC, animated: true)
    }
    
    @objc private func addItemButtonTapped() {
        // Navigate to add item page
        let addItemVC = AddItemViewController(groupId: groupDetail.id, groupName: groupDetail.name)
        let navController = UINavigationController(rootViewController: addItemVC)
        present(navController, animated: true)
    }
    
    @objc private func itemWasAdded() {
        loadActualItemsSimple()
    }
    
    @objc private func groupWasUpdated(_ notification: Notification) {
        // If we receive an updated GroupDetail, update UI immediately
        if let updated = notification.object as? GroupDetail, updated.id == self.groupDetail.id {
            self.groupDetail = updated
            setupData()
            itemsTableView.reloadData()
        } else {
            // Fallback: re-fetch from server
            loadActualItemsSimple()
        }
    }
    
    private func loadActualItemsSimple() {
        
        Task {
            do {
                let actualItems = try await NetworkManager.shared.getItemsForGroup(groupId: self.groupDetail.id)
                
                await MainActor.run {
                    self.updateItemsDisplay(with: actualItems)
                }
            } catch {
                await MainActor.run {
                    // Just show empty state, no error dialog
                    self.updateItemsDisplay(with: [])
                }
            }
        }
    }

    @objc private func deleteButtonTapped() {
        showDeleteConfirmation()
    }
    
    @objc private func locationButtonTapped() {
        openLocationInMaps()
    }
    
    private func openLocationInMaps() {
        // Check if we have coordinates or at least an address
        let hasCoordinates = groupDetail.latitude != nil && groupDetail.longitude != nil && 
                           groupDetail.latitude != 0 && groupDetail.longitude != 0
        let hasAddress = groupDetail.locationAddress != nil && !groupDetail.locationAddress!.isEmpty
        
        guard hasCoordinates || hasAddress else {
            showAlert(title: "Location Error", message: "No valid location data available for this group.")
            return
        }
        
        // Create the URL for maps
        let address: String
        if let locationAddress = groupDetail.locationAddress, !locationAddress.isEmpty {
            address = locationAddress
        } else if let latitude = groupDetail.latitude, let longitude = groupDetail.longitude {
            address = "\(latitude),\(longitude)"
        } else {
            showAlert(title: "Location Error", message: "No valid location data available for this group.")
            return
        }
        
        let encodedAddress = address.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? address
        
        // Try Google Maps app first, then fall back to other options
        if let googleMapsURL = URL(string: "comgooglemaps://?q=\(encodedAddress)"),
           UIApplication.shared.canOpenURL(googleMapsURL) {
            UIApplication.shared.open(googleMapsURL)
        } else if let googleMapsWebURL = URL(string: "https://maps.google.com/?q=\(encodedAddress)") {
            UIApplication.shared.open(googleMapsWebURL)
        } else if hasCoordinates, let latitude = groupDetail.latitude, let longitude = groupDetail.longitude,
                  let appleMapsURL = URL(string: "http://maps.apple.com/?q=\(latitude),\(longitude)") {
            UIApplication.shared.open(appleMapsURL)
        } else if let appleMapsURL = URL(string: "http://maps.apple.com/?q=\(encodedAddress)") {
            UIApplication.shared.open(appleMapsURL)
        } else {
            showAlert(title: "Maps Error", message: "Unable to open maps application.")
        }
    }
    
    private func loadActualItems() {
        // Show loading indicator
        let loadingAlert = UIAlertController(title: "Loading Items...", message: nil, preferredStyle: .alert)
        present(loadingAlert, animated: true)
        
        
        Task {
            do {
                // Add timeout protection
                let actualItems = try await withTimeout(seconds: 10) {
                    try await NetworkManager.shared.getItemsForGroup(groupId: self.groupDetail.id)
                }
                
                
                await MainActor.run {
                    loadingAlert.dismiss(animated: true) {
                        self.updateItemsDisplay(with: actualItems)
                    }
                }
            } catch {
                
                await MainActor.run {
                    loadingAlert.dismiss(animated: true) {
                        // Show items that were already loaded (fallback)
                        if !self.groupDetail.items.isEmpty {
                            self.updateItemsDisplay(with: self.groupDetail.items)
                        } else {
                            self.showAlert(title: "Error", message: "Failed to load items: \(error.localizedDescription)")
                        }
                    }
                }
            }
        }
    }
    
    // Helper function to add timeout to async operations
    private func withTimeout<T>(seconds: TimeInterval, operation: @escaping () async throws -> T) async throws -> T {
        return try await withThrowingTaskGroup(of: T.self) { group in
            // Add the main operation
            group.addTask {
                try await operation()
            }
            
            // Add timeout task
            group.addTask {
                try await Task.sleep(nanoseconds: UInt64(seconds * 1_000_000_000))
                throw NetworkError.serverError("Operation timed out after \(seconds) seconds")
            }
            
            // Return the first result and cancel the other task
            let result = try await group.next()!
            group.cancelAll()
            return result
        }
    }
    
    private func updateItemsDisplay(with items: [GroupItem]) {
        // Create a new GroupDetail with the actual items
        let updatedGroupDetail = GroupDetail(
            id: groupDetail.id,
            name: groupDetail.name,
            date: groupDetail.date,
            price: groupDetail.price,
            totalItems: groupDetail.totalItems,
            totalSoldItems: groupDetail.totalSoldItems,
            soldPrice: groupDetail.soldPrice,
            items: items,
            imageFilename: groupDetail.imageFilename,
            latitude: groupDetail.latitude,
            longitude: groupDetail.longitude,
            locationAddress: groupDetail.locationAddress
        )
        
        // Update the groupDetail property
        self.groupDetail = updatedGroupDetail
        
        // Reload the table view
        itemsTableView.reloadData()
        
        // Update the items label
        itemsLabel.text = "📦 Items (\(items.count))"
        
        // Update table view height - remove old constraint first
        for constraint in itemsTableView.constraints {
            if constraint.firstAttribute == .height {
                itemsTableView.removeConstraint(constraint)
            }
        }
        
        // Add new height constraint
        let newHeightConstraint = itemsTableView.heightAnchor.constraint(equalToConstant: CGFloat(max(items.count * 50, 50)))
        newHeightConstraint.isActive = true
        
    }
    
    private func showAlert(title: String, message: String) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
    
    private func showDeleteConfirmation() {
        let alert = UIAlertController(
            title: "Delete Group",
            message: "Are you sure you want to delete '\(groupDetail.name)'? This action cannot be undone.",
            preferredStyle: .alert
        )
        
        alert.addAction(UIAlertAction(title: "Cancel", style: .cancel))
        alert.addAction(UIAlertAction(title: "Delete", style: .destructive) { _ in
            self.deleteGroup()
        })
        
        present(alert, animated: true)
    }
    
    private func deleteGroup() {
        // Show loading indicator
        let loadingAlert = UIAlertController(title: "Deleting Group...", message: nil, preferredStyle: .alert)
        present(loadingAlert, animated: true)
        
        Task {
            do {
                try await NetworkManager.shared.removeGroup(groupId: groupDetail.id)
                
                await MainActor.run {
                    loadingAlert.dismiss(animated: true) {
                        // Post notification that group was deleted
                        NotificationCenter.default.post(name: .groupDeleted, object: nil)
                        
                        // Show success message and dismiss
                        let successAlert = UIAlertController(
                            title: "Success",
                            message: "Group '\(self.groupDetail.name)' has been deleted.",
                            preferredStyle: .alert
                        )
                        successAlert.addAction(UIAlertAction(title: "OK", style: .default) { _ in
                            self.navigationController?.popViewController(animated: true)
                        })
                        self.present(successAlert, animated: true)
                    }
                }
            } catch {
                await MainActor.run {
                    loadingAlert.dismiss(animated: true) {
                        let errorMessage: String
                        switch error {
                        case NetworkError.unauthorized:
                            errorMessage = "Please log in again to delete groups."
                        case NetworkError.serverError(let message):
                            errorMessage = "Server error: \(message)"
                        default:
                            errorMessage = "Failed to delete group. Please try again."
                        }
                        
                        self.showAlert(title: "Delete Failed", message: errorMessage)
                    }
                }
            }
        }
    }
    
    private func loadGroupImage() {
        guard let imageFilename = groupDetail.imageFilename, !imageFilename.isEmpty else {
            groupImageView.isHidden = true
            updateStatsViewConstraint(hasImage: false)
            return
        }
        
        
        // Show loading indicator
        imageActivityIndicator.startAnimating()
        groupImageView.isHidden = false
        
        // Construct image URL
        let imageURL = "https://gsale.levimylesllc.com/static/uploads/\(imageFilename)"
        
        guard let url = URL(string: imageURL) else {
            imageActivityIndicator.stopAnimating()
            groupImageView.isHidden = true
            return
        }
        
        // Load image asynchronously
        Task {
            do {
                let (data, response) = try await URLSession.shared.data(from: url)
                
                guard let httpResponse = response as? HTTPURLResponse,
                      httpResponse.statusCode == 200 else {
                    await MainActor.run {
                        imageActivityIndicator.stopAnimating()
                        groupImageView.isHidden = true
                        updateStatsViewConstraint(hasImage: false)
                    }
                    return
                }
                
                guard let image = UIImage(data: data) else {
                    await MainActor.run {
                        imageActivityIndicator.stopAnimating()
                        groupImageView.isHidden = true
                        updateStatsViewConstraint(hasImage: false)
                    }
                    return
                }
                
                await MainActor.run {
                    groupImageView.image = image
                    imageActivityIndicator.stopAnimating()
                    updateStatsViewConstraint(hasImage: true)
                    
                    // Animate the image appearance
                    groupImageView.alpha = 0
                    UIView.animate(withDuration: 0.3) {
                        self.groupImageView.alpha = 1
                    }
                }
                
            } catch {
                await MainActor.run {
                    imageActivityIndicator.stopAnimating()
                    groupImageView.isHidden = true
                    updateStatsViewConstraint(hasImage: false)
                }
            }
        }
    }
    
    private func updateStatsViewConstraint(hasImage: Bool) {
        // Deactivate the current constraint
        statsViewTopConstraint.isActive = false
        
        if hasImage {
            // Position stats view below the image
            statsViewTopConstraint = statsView.topAnchor.constraint(equalTo: groupImageView.bottomAnchor, constant: 20)
        } else {
            // Position stats view directly below the price (no spacing for image)
            statsViewTopConstraint = statsView.topAnchor.constraint(equalTo: priceLabel.bottomAnchor, constant: 20)
        }
        
        // Activate the new constraint
        statsViewTopConstraint.isActive = true
        
        // Animate the layout change
        UIView.animate(withDuration: 0.3) {
            self.view.layoutIfNeeded()
        }
    }
    
    private func hasLocationData() -> Bool {
        let hasCoordinates = groupDetail.latitude != nil && groupDetail.longitude != nil && groupDetail.latitude != 0 && groupDetail.longitude != 0
        let hasAddress = groupDetail.locationAddress != nil && !groupDetail.locationAddress!.isEmpty
        let hasLocation = hasCoordinates || hasAddress
        return hasLocation
    }
}

extension GroupDetailViewController: UITableViewDataSource {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return groupDetail.items.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "ItemCell", for: indexPath)
        let item = groupDetail.items[indexPath.row]
        
        // Clear any existing subviews
        cell.contentView.subviews.forEach { $0.removeFromSuperview() }
        
        // Create simple, clean layout with just the name
        let nameLabel = UILabel()
        nameLabel.text = item.name
        nameLabel.font = UIFont.systemFont(ofSize: 17, weight: .medium)
        nameLabel.textColor = .label
        nameLabel.translatesAutoresizingMaskIntoConstraints = false
        
        // Add status indicator dot
        let statusDot = UIView()
        statusDot.backgroundColor = item.sold ? .systemGreen : .systemBlue
        statusDot.layer.cornerRadius = 4
        statusDot.translatesAutoresizingMaskIntoConstraints = false
        
        // Add to cell
        cell.contentView.addSubview(statusDot)
        cell.contentView.addSubview(nameLabel)
        
        // Setup constraints
        NSLayoutConstraint.activate([
            statusDot.leadingAnchor.constraint(equalTo: cell.contentView.leadingAnchor, constant: 20),
            statusDot.centerYAnchor.constraint(equalTo: cell.contentView.centerYAnchor),
            statusDot.widthAnchor.constraint(equalToConstant: 8),
            statusDot.heightAnchor.constraint(equalToConstant: 8),
            
            nameLabel.leadingAnchor.constraint(equalTo: statusDot.trailingAnchor, constant: 12),
            nameLabel.trailingAnchor.constraint(equalTo: cell.contentView.trailingAnchor, constant: -50),
            nameLabel.centerYAnchor.constraint(equalTo: cell.contentView.centerYAnchor)
        ])
        
        // Cell styling
        cell.backgroundColor = .systemBackground
        cell.selectionStyle = .none
        cell.accessoryType = .disclosureIndicator
        
        // Add subtle highlight on selection
        let selectedBackgroundView = UIView()
        selectedBackgroundView.backgroundColor = .systemGray6
        cell.selectedBackgroundView = selectedBackgroundView
        
        return cell
    }
}

extension GroupDetailViewController: UITableViewDelegate {
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        
        let item = groupDetail.items[indexPath.row]
        
        // Fetch full item details from /items/describe
        showItemDetails(itemId: item.id, itemName: item.name)
    }
    
    private func showItemDetails(itemId: String, itemName: String) {
        // Show loading indicator
        let loadingAlert = UIAlertController(title: "Loading...", message: "Fetching item details", preferredStyle: .alert)
        present(loadingAlert, animated: true)
        
        Task {
            do {
                let itemDetail = try await NetworkManager.shared.getItemDetails(itemId: itemId)
                
                await MainActor.run {
                    loadingAlert.dismiss(animated: true) {
                        self.presentItemDetailAlert(itemDetail: itemDetail)
                    }
                }
            } catch {
                await MainActor.run {
                    loadingAlert.dismiss(animated: true) {
                        let errorAlert = UIAlertController(
                            title: "Error",
                            message: "Failed to load item details: \(error.localizedDescription)",
                            preferredStyle: .alert
                        )
                        errorAlert.addAction(UIAlertAction(title: "OK", style: .default))
                        self.present(errorAlert, animated: true)
                    }
                }
            }
        }
    }
    
    private func presentItemDetailAlert(itemDetail: ItemDetail) {
        var message = """
        🏷️ Category: \(itemDetail.category)
        📍 Storage: \(itemDetail.storage ?? "Not specified")
        📦 Status: \(itemDetail.sold ? "✅ Sold" : "📦 Available")
        🔄 Returned: \(itemDetail.returned ? "Yes" : "No")
        """
        
        // Add financial details if the item is sold
        if itemDetail.sold {
            var financialDetails = "\n\n💰 Sale Details:"
            var hasFinancialData = false
            
            if let soldPrice = itemDetail.soldPrice {
                financialDetails += "\n💵 Sold Price: $\(String(format: "%.2f", soldPrice))"
                hasFinancialData = true
            }
            
            if let shippingFee = itemDetail.shippingFee {
                financialDetails += "\n📦 Shipping Fee: $\(String(format: "%.2f", shippingFee))"
                hasFinancialData = true
            }
            
            if let netPrice = itemDetail.netPrice {
                financialDetails += "\n💰 Net Profit: $\(String(format: "%.2f", netPrice))"
                hasFinancialData = true
            }
            
            if let soldDate = itemDetail.soldDate {
                financialDetails += "\n📅 Sold Date: \(soldDate)"
                hasFinancialData = true
            }
            
            if let daysToSell = itemDetail.daysToSell {
                financialDetails += "\n⏱️ Days to Sell: \(daysToSell)"
                hasFinancialData = true
            }
            
            if hasFinancialData {
                message += financialDetails
            } else {
                message += "\n\n💰 Sale Details: Not available"
            }
        }
        
        let alert = UIAlertController(
            title: itemDetail.name,
            message: message,
            preferredStyle: .alert
        )
        
        // Add Sell action if item is not sold
        if !itemDetail.sold {
            alert.addAction(UIAlertAction(title: "Sell...", style: .default) { _ in
                let sellVC = SellItemViewController(itemId: itemDetail.id, itemName: itemDetail.name, groupId: itemDetail.groupId)
                self.navigationController?.pushViewController(sellVC, animated: true)
            })
        }

        // If sold, add Return action; else allow Sell
        if itemDetail.sold {
            alert.addAction(UIAlertAction(title: "↩️ Return (Mark Available)", style: .default) { _ in
                // Confirm return
                let confirm = UIAlertController(title: "Confirm Return", message: "Mark this item as available?", preferredStyle: .alert)
                confirm.addAction(UIAlertAction(title: "Cancel", style: .cancel))
                confirm.addAction(UIAlertAction(title: "Return", style: .destructive) { _ in
                    // Call API to mark available
                    let loading = UIAlertController(title: "Processing...", message: nil, preferredStyle: .alert)
                    self.present(loading, animated: true)
                    Task {
                        do {
                            try await NetworkManager.shared.markItemAvailable(itemId: itemDetail.id)
                            let updatedDetail = try await NetworkManager.shared.getItemDetails(itemId: itemDetail.id)
                            let updatedGroup = try await NetworkManager.shared.getGroupDetails(groupId: itemDetail.groupId)
                            await MainActor.run {
                                loading.dismiss(animated: true) {
                                    // Refresh group view
                                    self.groupDetail = updatedGroup
                                    self.setupData()
                                    self.itemsTableView.reloadData()
                                    self.showAlert(title: "Success", message: "Item marked as available.")
                                }
                            }
                        } catch {
                            await MainActor.run {
                                loading.dismiss(animated: true) {
                                    self.showAlert(title: "Error", message: "Failed to mark item as available.")
                                }
                            }
                        }
                    }
                })
                self.present(confirm, animated: true)
            })
        }

        // Add Remove Item action
        alert.addAction(UIAlertAction(title: "🗑️ Remove Item", style: .destructive) { _ in
            self.confirmRemoveItem(itemDetail: itemDetail)
        })
        
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
    
    private func confirmRemoveItem(itemDetail: ItemDetail) {
        let confirmAlert = UIAlertController(
            title: "Remove Item",
            message: "Are you sure you want to permanently remove '\(itemDetail.name)'? This action cannot be undone.",
            preferredStyle: .alert
        )
        
        confirmAlert.addAction(UIAlertAction(title: "Cancel", style: .cancel))
        
        confirmAlert.addAction(UIAlertAction(title: "Remove", style: .destructive) { _ in
            self.removeItem(itemDetail: itemDetail)
        })
        
        present(confirmAlert, animated: true)
    }
    
    private func removeItem(itemDetail: ItemDetail) {
        // Show loading indicator
        let loadingAlert = UIAlertController(title: "Removing Item...", message: nil, preferredStyle: .alert)
        present(loadingAlert, animated: true)
        
        Task {
            do {
                try await NetworkManager.shared.removeItem(itemId: itemDetail.id)
                
                await MainActor.run {
                    loadingAlert.dismiss(animated: true) {
                        // Show success message
                        let successAlert = UIAlertController(
                            title: "Success",
                            message: "'\(itemDetail.name)' has been removed successfully.",
                            preferredStyle: .alert
                        )
                        successAlert.addAction(UIAlertAction(title: "OK", style: .default) { _ in
                            // Refresh the items list to reflect the removal
                            self.loadActualItemsSimple()
                        })
                        self.present(successAlert, animated: true)
                    }
                }
            } catch {
                await MainActor.run {
                    loadingAlert.dismiss(animated: true) {
                        let errorMessage: String
                        switch error {
                        case NetworkError.unauthorized:
                            errorMessage = "Please log in again to remove items."
                        case NetworkError.serverError(let message):
                            errorMessage = "Server error: \(message)"
                        default:
                            errorMessage = "Failed to remove item. Please try again."
                        }
                        
                        let errorAlert = UIAlertController(
                            title: "Remove Failed",
                            message: errorMessage,
                            preferredStyle: .alert
                        )
                        errorAlert.addAction(UIAlertAction(title: "OK", style: .default))
                        self.present(errorAlert, animated: true)
                    }
                }
            }
        }
    }
} 

extension Notification.Name {
    static let groupUpdated = Notification.Name("groupUpdated")
} 
