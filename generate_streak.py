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
    svg_width, svg_height = 850, 180
    box_size, gap = 10, 4
    offset_x, offset_y = 40, 50
    
    font_family = "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
    
    svg = [f'<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">']
    
    # 배경
    svg.append('<rect width="100%" height="100%" fill="#0d1117" rx="6"/>')
    
    today = datetime.now()
    start_date = today - timedelta(days=365)
    start_date = start_date - timedelta(days=(start_date.weekday() + 1) % 7)
    
    # 그래프 영역 시작
    svg.append(f'<g transform="translate({offset_x}, {offset_y})">')
    
    # 좌측 요일 라벨 (인라인 스타일 적용)
    svg.append(f'<text text-anchor="end" dx="-10" dy="22" font-size="9" fill="#7d8590" font-family="{font_family}">Mon</text>')
    svg.append(f'<text text-anchor="end" dx="-10" dy="50" font-size="9" fill="#7d8590" font-family="{font_family}">Wed</text>')
    svg.append(f'<text text-anchor="end" dx="-10" dy="78" font-size="9" fill="#7d8590" font-family="{font_family}">Fri</text>')
    
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    last_month = -1
    last_year = -1
    
    for week in range(53):
        group_x = week * (box_size + gap)
        svg.append(f'<g transform="translate({group_x}, 0)">')
        
        for day in range(7):
            current_date = start_date + timedelta(weeks=week, days=day)
            if current_date > today:
                break
                
            # 상단 년도 및 월 라벨 (2단 표기)
            if day == 0:
                current_month = current_date.month
                current_year = current_date.year
                if (current_month != last_month or current_year != last_year) and week < 52:
                    # 년도 (상단)
                    svg.append(f'<text x="0" y="-22" font-size="10" fill="#7d8590" font-family="{font_family}">{current_year}</text>')
                    # 월 (하단)
                    svg.append(f'<text x="0" y="-10" font-size="10" fill="#7d8590" font-family="{font_family}">{month_names[current_month - 1]}</text>')
                    last_month = current_month
                    last_year = current_year

            date_str = current_date.strftime("%Y-%m-%d")
            count = counts.get(date_str, 0)
            
            # 커밋 개수에 따른 색상 지정 로직
            if count == 0: color_idx = 0
            elif count <= 1: color_idx = 1
            elif count <= 2: color_idx = 2
            elif count <= 3: color_idx = 3
            else: color_idx = 4
            
            color = colors[color_idx]
            y_pos = day * (box_size + gap)
            svg.append(f'<rect width="{box_size}" height="{box_size}" y="{y_pos}" fill="{color}" rx="2"/>')
            
        svg.append('</g>')
        
    svg.append('</g>')
    
    # 우측 하단 범례 (인라인 스타일 적용)
    legend_x = svg_width - 160
    legend_y = svg_height - 25
    svg.append(f'<g transform="translate({legend_x}, {legend_y})">')
    svg.append(f'<text x="-25" y="9" font-size="9" fill="#7d8590" font-family="{font_family}">Less</text>')
    
    for i, color in enumerate(colors):
        rect_x = i * (box_size + gap)
        svg.append(f'<rect width="{box_size}" height="{box_size}" x="{rect_x}" y="0" fill="{color}" rx="2"/>')
        
    svg.append(f'<text x="{5 * (box_size + gap) + 5}" y="9" font-size="9" fill="#7d8590" font-family="{font_family}">More</text>')
    svg.append('</g>')
    
    svg.append('</svg>')
    
    with open("streak.svg", "w") as f:
        f.write("\n".join(svg))

if __name__ == "__main__":
    commit_counts = get_commit_data()
    generate_svg(commit_counts)
