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
	ch = soup.find('table','css')
	if (ch == None):
		return cList
	for t in ch.find_all('a'):
		h = t.get('href')
		url = f'{h}'
		#print(url)
		#print(t)
		cList.append(url)
	#print (cList)
	return cList

def findTitle(soup): #小說名稱
	if (soup == None):
		return "not found!"
	t =	soup.find('div', {"id": "title"})
	#print (t)
	if (t != None):
		print (t.text)
		return t.text
		
	return t
	
def findChapN(soup,title): #章節名稱
	cn = soup.find('div', {"id": "title"})
	#print(cn.text)
	#lines = cn.text.split('\n')

	return(cn.text)

def findContent(soup): #小說內容
	cnt = soup.find('div',{"id": "content"}).text
	return cnt

def multiTa(chapL,title,temp): #Multiprocess func
	url=chapL[temp]
	r = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	resp=urllib2.urlopen(r)
	soup = BeautifulSoup(resp, 'lxml',from_encoding="gb18030")
	fileA=open(f'temp/temp{temp+1}.txt','w',encoding='utf-8')
	print ('.', end='',flush=True)
	#print (url)
	fileA.write(findChapN(soup,title)+'\n\n\n\n')
	contents=findContent(soup).splitlines()
	for line in contents: #排版
		if line != '':
			fileA.write('       '+line.strip()+'\n\n')
	fileA.close()
	
def mergeN(title,count): #暫存檔合體
	fileT=open(f"src/{keyW}_{title}.txt","w",encoding="utf-8")
	for i in range(1,count):
		fileA=open(f"temp/temp{i}.txt","r",encoding="utf-8")
		fileT.write(fileA.read()+'\n\n\n\n\n')
		fileA.close()
		#os.remove(f'temp/temp{i}.txt')
	
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
	keyW='2152' #替換成要下載小說 https://czbooks.net/n/u55bm 連結最後這一段
	if (len(sys.argv) >1):
		if (sys.argv[1] != None):
			keyW=sys.argv[1]
	else:
		print ("usage: %s id \nex. %s %s" %(sys.argv[0], sys.argv[0], keyW))
		print ("https://www.wenku8.net/ downloader")
		print ("https://www.wenku8.net/register.php  to register a new account")
	#print (len(sys.argv))	
	url=f'https://www.wenku8.net/modules/article/reader.php?aid={keyW}'
	print(url)
	r = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	page = urllib2.urlopen(r);
	soup = BeautifulSoup(page,features="lxml",from_encoding="gb18030")

	#print (url)
	#soup = BeautifulSoup(fetch(url),from_encoding="gb18030")
	
	#print (soup.title)
	
	chapL=getChapList(soup)
	#print (chapL)
	
	if (chapL != None and len(chapL) != 0):
		title=findTitle(soup)
		if (title != None):
			pool = multiprocessing.Pool()
			pool.map(partial(multiTa,chapL,title), range(0,len(chapL)))
			pool.close()
	
			mergeN(title,len(chapL)+1)
			print('\nDone!')
		else:
			print ("Title not found!!")
	
	else:
		print ("No Chapter found!!")
