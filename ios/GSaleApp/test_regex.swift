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

// Test the current regex pattern
let itemPattern = #"<tr[^>]*>[\s\S]*?<td[^>]*>(\d+)</td>[\s\S]*?<td[^>]*><a[^>]*href\s*=\s*"[^"]*item=([^"&]+)"[^>]*>([^<]+)</a></td>[\s\S]*?<td[^>]*><a[^>]*href[^>]*>([^<]+)</a></td>[\s\S]*?<td[^>]*><a[^>]*href[^>]*>([^<]+)</a></td>[\s\S]*?<td[^>]*>([^<]*?)</td>[\s\S]*?<td[^>]*>([^<]*?)</td>[\s\S]*?<td[^>]*>([^<]*?)</td>[\s\S]*?<td[^>]*><a[^>]*href\s*=\s*"[^"]*storage=([^"]*)"[^>]*>([^<]*)</a></td>[\s\S]*?<td[^>]*><a[^>]*href\s*=\s*"[^"]*group_id=([^"&]+)"[^>]*>([^<]+)</a></td>[\s\S]*?</tr>"#

do {
    let regex = try NSRegularExpression(pattern: itemPattern, options: [.dotMatchesLineSeparators])
    let matches = regex.matches(in: html, options: [], range: NSRange(html.startIndex..<html.endIndex, in: html))
    
    print("Found \(matches.count) matches")
    
    for match in matches {
        print("Match has \(match.numberOfRanges) groups")
        if match.numberOfRanges >= 3 {
            let itemIdRange = Range(match.range(at: 2), in: html)!
            let nameRange = Range(match.range(at: 3), in: html)!
            let itemId = String(html[itemIdRange])
            let name = String(html[nameRange])
            print("Found: \(name) (\(itemId))")
        }
    }
} catch {
    print("Regex error: \(error)")
}
