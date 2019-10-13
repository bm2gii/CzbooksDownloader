import requests
from bs4 import BeautifulSoup
import os
from functools import partial
import multiprocessing 
from multiprocessing import Pool
import time
import re

def fetch(url):
	headers={'User-Agent': "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"}
	resp=requests.get(url,headers=headers).text
	return resp

def getChapList(soup): #找出網頁的章節連結
	cList=[]
	for t in soup.find('ul','nav chapter-list').find_all('a'):
		cList.append(t.get('href'))
	return cList

def findTitle(soup): #小說名稱
	return soup.find('span','title').text
	
def findChapN(soup,title): #章節名稱
	return(soup.find('div','name').text.replace(title,''))

def findContent(soup): #小說內容
	return(soup.find('div','content').text)

def multiTa(chapL,title,temp): #Multiprocess func
	url='https:'+chapL[temp]
	resp=fetch(url)
	soup = BeautifulSoup(resp, 'html.parser')
	fileA=open(f"temp/temp{temp+1}.txt","w",encoding="utf-8")
	
	fileA.write(findChapN(soup,title)+'\n\n\n\n')
	contents=findContent(soup).splitlines()
	for line in contents: #排版
		if line != '':
			fileA.write('       '+line.strip()+'\n\n')
	fileA.close()
	
def mergeN(title,count): #暫存檔合體
	fileT=open(f"src/{title}.txt","w",encoding="utf-8")
	for i in range(1,count):
		fileA=open(f"temp/temp{i}.txt","r",encoding="utf-8")
		fileT.write(fileA.read()+'\n\n\n\n\n')
		fileA.close()
		os.remove(f'temp/temp{i}.txt')
	
	fileT.close()
	
if __name__ == '__main__':

	if(not os.path.exists('src')):	
		os.mkdir('src')
	if(not os.path.exists('temp')):	
		os.mkdir('temp')
	keyW='ujbc0' #替換成要下載小說 https://czbooks.net/n/u55bm 連結最後這一段
	url=f'https://czbooks.net/n/{keyW}'
	resp=fetch(url)
	soup = BeautifulSoup(resp, 'html.parser')
	
	chapL=getChapList(soup)
	title=findTitle(soup)
	
	pool = multiprocessing.Pool()
	pool.map(partial(multiTa,chapL,title), range(0,len(chapL)))
	pool.close()
	
	mergeN(title,len(chapL)+1)
	
