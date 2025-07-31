import Foundation

let html = """
        <tr>
            <td>2</td>
            <td><a href = "/items/describe?item=a448055c-710a-449d-b1f0-7ec3ffe24d8a">pika</a></td>
            <td><a href = "/items/list?purchase_date=2025-07-31">2025-07-31</a></td>
            <td><a href = "/items/list?list_date=2025-07-31">2025-07-31</a></td>
            
                <td>NA</td>
                <td>NA</td>
                <td>0</td>
            
            <td><a href = "/items/list?storage="></a></td>
            <td><a href = "/groups/describe?group_id=1601669c-eade-49c5-8cf6-fb56e384aca6">2025-07-31-games</a></td>
            <td><a href= "/items/remove?id=a448055c-710a-449d-b1f0-7ec3ffe24d8a">remove</a></td>
            </tr>
"""

// Test the updated regex pattern (same as current)
let itemPattern = #"<tr[^>]*>[\s\S]*?<td[^>]*>(\d+)</td>[\s\S]*?<td[^>]*><a[^>]*href\s*=\s*"[^"]*item=([^"&]+)"[^>]*>([^<]+)</a></td>[\s\S]*?<td[^>]*><a[^>]*href[^>]*>([^<]+)</a></td>[\s\S]*?<td[^>]*><a[^>]*href[^>]*>([^<]+)</a></td>[\s\S]*?<td[^>]*>([^<]*?)</td>[\s\S]*?<td[^>]*>([^<]*?)</td>[\s\S]*?<td[^>]*>([^<]*?)</td>[\s\S]*?<td[^>]*><a[^>]*href\s*=\s*"[^"]*storage=([^"]*)"[^>]*>([^<]*)</a></td>[\s\S]*?<td[^>]*><a[^>]*href\s*=\s*"[^"]*group_id=([^"&]+)"[^>]*>([^<]+)</a></td>[\s\S]*?</tr>"#

do {
    let regex = try NSRegularExpression(pattern: itemPattern, options: [.dotMatchesLineSeparators])
    let matches = regex.matches(in: html, options: [], range: NSRange(html.startIndex..<html.endIndex, in: html))
    
    print("Found \(matches.count) matches")
    
    for match in matches {
        print("Match has \(match.numberOfRanges) groups")
        if match.numberOfRanges >= 13 {
            let indexRange = Range(match.range(at: 1), in: html)!
            let itemIdRange = Range(match.range(at: 2), in: html)!
            let nameRange = Range(match.range(at: 3), in: html)!
            let purchaseDateRange = Range(match.range(at: 4), in: html)!
            let listDateRange = Range(match.range(at: 5), in: html)!
            let soldDateRange = Range(match.range(at: 6), in: html)!
            let daysToSellRange = Range(match.range(at: 7), in: html)!
            let soldNetRange = Range(match.range(at: 8), in: html)!
            let storageValueRange = Range(match.range(at: 9), in: html)!
            let storageTextRange = Range(match.range(at: 10), in: html)!
            let groupIdRange = Range(match.range(at: 11), in: html)!
            let groupNameRange = Range(match.range(at: 12), in: html)!
            
            let index = String(html[indexRange])
            let itemId = String(html[itemIdRange])
            let name = String(html[nameRange])
            let purchaseDate = String(html[purchaseDateRange])
            let listDate = String(html[listDateRange])
            let soldDate = String(html[soldDateRange])
            let daysToSell = String(html[daysToSellRange])
            let soldNet = String(html[soldNetRange])
            let storageValue = String(html[storageValueRange])
            let storageText = String(html[storageTextRange])
            let groupId = String(html[groupIdRange])
            let groupName = String(html[groupNameRange])
            
            print("Index: '\(index)'")
            print("Name: '\(name)' ID: '\(itemId)'")
            print("Purchase: '\(purchaseDate)' List: '\(listDate)'")
            print("Sold: '\(soldDate)' Days: '\(daysToSell)' Net: '\(soldNet)'")
            print("Storage Value: '\(storageValue)' Text: '\(storageText)'")
            print("Group: '\(groupName)' (\(groupId))")
        }
    }
} catch {
    print("Regex error: \(error)")
}
