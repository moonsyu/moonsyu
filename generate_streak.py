import requests
from datetime import datetime, timedelta
import os

USERNAME = "moonsyu"
REPO = "BackJoonCode"
TOKEN = os.getenv("GITHUB_TOKEN")

def get_commit_data():
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
    since = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%dT%H:%M:%SZ')
    url = f"https://api.github.com/repos/{USERNAME}/{REPO}/commits?since={since}&per_page=100"
    
    counts = {}
    while url:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            break
        for item in res.json():
            date = item['commit']['author']['date'][:10]
            counts[date] = counts.get(date, 0) + 1
        
        url = res.links.get('next', {}).get('url')
    return counts

def generate_svg(counts):
    colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
    svg_width, svg_height = 800, 150
    box_size, gap = 10, 4
    
    svg = [f'<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">']
    svg.append('<rect width="100%" height="100%" fill="#0d1117" rx="6"/>')
    svg.append('<g transform="translate(30, 20)">')
    
    today = datetime.now()
    start_date = today - timedelta(days=365)
    start_date = start_date - timedelta(days=(start_date.weekday() + 1) % 7) # 일요일 시작
    
    for week in range(53):
        svg.append(f'<g transform="translate({week * (box_size + gap)}, 0)">')
        for day in range(7):
            current_date = start_date + timedelta(weeks=week, days=day)
            if current_date > today:
                break
                
            date_str = current_date.strftime("%Y-%m-%d")
            count = counts.get(date_str, 0)
            
            color_idx = min(4, (count + 1) // 2) if count > 0 else 0
            color = colors[color_idx]
            
            y_pos = day * (box_size + gap)
            svg.append(f'<rect width="{box_size}" height="{box_size}" y="{y_pos}" fill="{color}" rx="2"/>')
        svg.append('</g>')
        
    svg.append('</g></svg>')
    
    with open("streak.svg", "w") as f:
        f.write("\n".join(svg))

if __name__ == "__main__":
    commit_counts = get_commit_data()
    generate_svg(commit_counts)
