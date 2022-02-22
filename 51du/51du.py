#coding=utf-8
from urllib.request import urlopen, Request
import urllib.request as urllib2
import requests
from bs4 import BeautifulSoup
import os
from functools import partial
import multiprocessing 
from multiprocessing import Pool
import time
import re
import sys, getopt
import codecs

debug = 0

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

def fetch(url):
	headers={'User-Agent': "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"}
	resp = ""
	if os.path.isfile('d:\\tmp\\cacert.pem'):
		resp=requests.get(url,headers=headers, verify='d:\\tmp\\cacert.pem').text
	else:
		resp=requests.get(url,headers=headers).text
	return resp

def getChapList(soup): #找出網頁的章節連結
	cList=[]
	#print(soup)
	ch = soup.find('div',{'class': 'mulu'})
	#print (ch)
	if (ch == None):
		return cList
	for t in ch.find_all('a'):
		h = t.get('href')
		url = f'{h}'
		#url = f'{h}'
		if debug: print(url)
		#print(t)
		cList.append(url)
	#print (cList)
	return cList

def findTitle(soup): #小說名稱
	if (soup == None):
		return "not found!"
	t =	soup.title.text
	if debug: print (t)
	if (t != None):
		lines = t.split('-')
		if debug: print (lines)
		print (lines[0])
		#return None
		return lines[0]
		
	return t
	
def findChapN(soup,title): #章節名稱
	if debug: print(soup)
	cn = soup.title.text
	if debug: print(cn)
	lines = cn.split('-')
	if debug: print(lines)
	if debug: print(lines[0])
	return lines[0]

def findContent(soup): #小說內容
	cnt = soup.find('div','yd_text2').text
	return cnt

def check_next_page(soup): #find if there is next page
	n = soup.find('div','pt-read-btn')
	#print(n)
	if n != None:
		#for t in n.find_all('a'):
		#	print(t.get('href'))
		
		nl = n.find('a', 'pt-nextchapter')
		#print(nl)
		h = nl.get('href')
		#print(n.text)
		#print (n.text.find('下一頁'))
		if (0 < n.text.find('下一頁')):
			url = f'https://www.twfanti.com{h}'
			return url

	return None
def multiTa(chapL,title,temp): #Multiprocess func
	if (type(chapL) == str):
		url = chapL
	else:
		url=chapL[temp]
	print(temp, url,flush=True)
	ret = temp + 1
	r = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
	#resp=urllib2.urlopen(r)
	
	try:
		resp=urllib2.urlopen(r)
		time.sleep(2)
	except Exception as e:
		print(e)
		print("wait 5 sec and try again")
		try:
			time.sleep(5)
			resp=urllib2.urlopen(r)
		except Exception as e:
			print("get %s again error!" %(url))
			return ret
	
	soup = BeautifulSoup(resp, 'lxml')
	fileA=open(f'temp/temp{temp+1}.txt','w',encoding='utf-8')
	#print ('.', end='',flush=True)
	#print (url)
	#print(soup)
	fileA.write(findChapN(soup,title)+'\n\n\n\n')
	contents=findContent(soup).splitlines()
	for line in contents: #排版
		if line != '':
			fileA.write('       '+line.strip()+'\n\n')
	fileA.close()
	#check next page

	next_page = check_next_page(soup)
	if (next_page != None):
		#print ('next_page=', next_page)
		ret = multiTa(next_page,title,ret)
	return ret

def mergeN(title,count): #暫存檔合體
	print('merg ', title, count)
	fileT=open(f"src/{title}.txt","w",encoding="utf-8")
	for i in range(1,count):
		fileA=open(f"temp/temp{i}.txt","r",encoding="utf-8")
		fileT.write(fileA.read()+'\n\n\n\n\n')
		fileA.close()
		os.remove(f'temp/temp{i}.txt')
	
	fileT.close()
	

	
if __name__ == '__main__':

	# Pyinstaller fix
	multiprocessing.freeze_support()

	if(not os.path.exists('src')):	
		os.mkdir('src')
	if(not os.path.exists('temp')):	
		os.mkdir('temp')
        
	#print (sys.argv[1])
	#https://www.wenku8.net/novel/2/2147/index.htm
	keyW='90HouFengShuiShi' #替換成要下載小說 https://czbooks.net/n/u55bm 連結最後這一段
	keyW='ChaoWeiLieXi' #替換成要下載小說 https://czbooks.net/n/u55bm 連結最後這一段
	if (len(sys.argv) >1):
		if (sys.argv[1] != None):
			keyW=sys.argv[1]
	else:
		print ("usage: %s id \nex. %s %s" %(sys.argv[0], sys.argv[0], keyW))
		print ("https:///www.51du.org/ downloader")
	#print (len(sys.argv))	
	url=f'https://www.51du.org/xs/{keyW}.html'
	print(url,flush=True)
	r = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	page = urllib2.urlopen(r);
	#soup = BeautifulSoup(page,features="lxml",from_encoding="gb18030")
	soup = BeautifulSoup(page,features="lxml")

	#print (url)
	#soup = BeautifulSoup(fetch(url),from_encoding="gb18030")
	
	#print (soup.title)
	
	chapL=getChapList(soup)
	#print (chapL)
	
	#for xx in chapL:
	#	print(xx)

	if (chapL != None and len(chapL) != 0):
		title=findTitle(soup)
		if (title != None):
			#pool = multiprocessing.Pool(1)
			#pool.map(partial(multiTa,chapL,title), range(0,len(chapL)))
			#pool.close()
			ret = 0
			for idx, ch in enumerate(chapL, start=0):
				ret = multiTa(ch, title, ret)
			#ret = multiTa(chapL[0], title, 0)
	
			mergeN(title,ret+1)
			print('\nDone!')
		else:
			print ("Title not found!!")
	
	else:
		print ("No Chapter found!!")
