import UIKit

class GroupsViewController: UIViewController {
    
    private let tableView = UITableView()
    private let addButton = UIBarButtonItem(barButtonSystemItem: .add, target: nil, action: nil)
    private let refreshControl = UIRefreshControl()
    private let activityIndicator = UIActivityIndicatorView(style: .large)
    
    private var groups: [Group] = []
    private var isLoading = false
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        loadGroups()
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        loadGroups()
    }
    
    private func setupUI() {
        view.backgroundColor = .systemBackground
        title = "Groups"
        
        navigationItem.rightBarButtonItem = addButton
        addButton.target = self
        addButton.action = #selector(addGroupTapped)
        
        tableView.delegate = self
        tableView.dataSource = self
        tableView.register(UITableViewCell.self, forCellReuseIdentifier: "GroupCell")
        tableView.translatesAutoresizingMaskIntoConstraints = false
        
        refreshControl.addTarget(self, action: #selector(refreshData), for: .valueChanged)
        tableView.refreshControl = refreshControl
        
        activityIndicator.hidesWhenStopped = true
        activityIndicator.translatesAutoresizingMaskIntoConstraints = false
        
        view.addSubview(tableView)
        view.addSubview(activityIndicator)
        
        NSLayoutConstraint.activate([
            tableView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            tableView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            tableView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            tableView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            
            activityIndicator.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            activityIndicator.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }
    
    @objc private func addGroupTapped() {
        let addGroupVC = AddGroupViewController()
        let navController = UINavigationController(rootViewController: addGroupVC)
        present(navController, animated: true)
    }
    
    @objc private func refreshData() {
        loadGroups()
    }
    
    private func loadGroups() {
        guard !isLoading else { return }
        
        isLoading = true
        print("🔄 Loading groups...")
        activityIndicator.startAnimating()
        
        Task {
            do {
                let fetchedGroups = try await NetworkManager.shared.getGroups()
                
                await MainActor.run {
                    self.groups = fetchedGroups
                    print("✅ Loaded \(fetchedGroups.count) groups")
                    self.tableView.reloadData()
                    self.refreshControl.endRefreshing()
                    self.activityIndicator.stopAnimating()
                    self.isLoading = false
                    
                    if fetchedGroups.isEmpty {
                        self.showAlert(title: "No Groups", message: "You don't have any groups yet. Tap the + button to create your first group!")
                    }
                }
            } catch {
                await MainActor.run {
                    print("❌ Failed to load groups: \(error)")
                    self.refreshControl.endRefreshing()
                    self.activityIndicator.stopAnimating()
                    self.isLoading = false
                    self.showAlert(title: "Error", message: "Failed to load groups. Please try again.")
                }
            }
        }
    }
    
    private func showAlert(title: String, message: String) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
}

extension GroupsViewController: UITableViewDataSource {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        print("📊 Table view asking for \(groups.count) rows")
        return groups.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "GroupCell", for: indexPath)
        let group = groups[indexPath.row]
        
        cell.textLabel?.text = group.name
        cell.detailTextLabel?.text = group.description ?? "Created: \(group.created_at)"
        cell.accessoryType = .disclosureIndicator
        
        print("📱 Configuring cell for group: \(group.name) - \(group.description ?? "no description")")
        return cell
    }
    
    func tableView(_ tableView: UITableView, titleForHeaderInSection section: Int) -> String? {
        if groups.isEmpty {
            return "No Groups Found"
        }
        return nil
    }
}

extension GroupsViewController: UITableViewDelegate {
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        
        let group = groups[indexPath.row]
        showGroupDetails(groupId: group.id)
    }
    
    private func showGroupDetails(groupId: String) {
        Task {
            do {
                let groupDetail = try await NetworkManager.shared.getGroupDetails(groupId: groupId)
                
                await MainActor.run {
                    let detailVC = GroupDetailViewController(groupDetail: groupDetail)
                    self.navigationController?.pushViewController(detailVC, animated: true)
                }
            } catch {
                await MainActor.run {
                    self.showAlert(title: "Error", message: "Failed to load group details. Please try again.")
                }
            }
        }
    }
} 