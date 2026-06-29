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
    offset_x, offset_y = 40, 50 # 텍스트가 들어갈 상단, 좌측 여백 추가
    
    svg = [f'<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">']
    
    # 텍스트 스타일 정의
    svg.append('''<style>
        .month { font-size: 10px; fill: #7d8590; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }
        .wday { font-size: 9px; fill: #7d8590; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }
        .title { font-size: 14px; font-weight: bold; fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }
    </style>''')
    
    # 배경
    svg.append('<rect width="100%" height="100%" fill="#0d1117" rx="6"/>')
    
    today = datetime.now()
    start_date = today - timedelta(days=365)
    start_date = start_date - timedelta(days=(start_date.weekday() + 1) % 7) # 일요일 시작 기준
    
    # 상단 연도 및 총 커밋 수 텍스트 추가
    total_commits = sum(counts.values())
    current_year = today.year
    svg.append(f'<text x="20" y="30" class="title">{total_commits} contributions in the last year ({current_year})</text>')
    
    # 그래프 영역 시작
    svg.append(f'<g transform="translate({offset_x}, {offset_y})">')
    
    # 좌측 요일 라벨 (Mon, Wed, Fri)
    svg.append('<text text-anchor="end" class="wday" dx="-10" dy="22">Mon</text>')
    svg.append('<text text-anchor="end" class="wday" dx="-10" dy="50">Wed</text>')
    svg.append('<text text-anchor="end" class="wday" dx="-10" dy="78">Fri</text>')
    
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    last_month = -1
    
    for week in range(53):
        group_x = week * (box_size + gap)
        svg.append(f'<g transform="translate({group_x}, 0)">')
        
        for day in range(7):
            current_date = start_date + timedelta(weeks=week, days=day)
            if current_date > today:
                break
                
            # 상단 월 라벨 (달이 바뀔 때 한 번만 표시)
            if day == 0:
                current_month = current_date.month
                if current_month != last_month and week < 52:
                    svg.append(f'<text x="0" y="-10" class="month">{month_names[current_month - 1]}</text>')
                    last_month = current_month

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
    
    # 우측 하단 범례 (Less ... More)
    legend_x = svg_width - 160
    legend_y = svg_height - 25
    svg.append(f'<g transform="translate({legend_x}, {legend_y})">')
    svg.append('<text x="-25" y="9" class="wday">Less</text>')
    
    for i, color in enumerate(colors):
        rect_x = i * (box_size + gap)
        svg.append(f'<rect width="{box_size}" height="{box_size}" x="{rect_x}" y="0" fill="{color}" rx="2"/>')
        
    svg.append(f'<text x="{5 * (box_size + gap) + 5}" y="9" class="wday">More</text>')
    svg.append('</g>')
    
    svg.append('</svg>')
    
    with open("streak.svg", "w") as f:
        f.write("\n".join(svg))

if __name__ == "__main__":
    commit_counts = get_commit_data()
    generate_svg(commit_counts)
