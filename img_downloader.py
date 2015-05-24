import requests, os, glob, sys, praw, shutil
from bs4 import BeautifulSoup

#subreddit specified
targetSubreddit = 'earthporn'
    
def downloadImage(imageUrl, localFileName):
    response = requests.get(imageUrl, stream = True)
    dir_name = "/Users/Guevara/Desktop/Wallpapers/"
    if response.status_code == 200:
        print('Downloading %s...' % (localFileName))
        with open(dir_name + localFileName, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response

r = praw.Reddit(user_agent='Test Script by /u/kevguev')
submissions = r.get_subreddit(targetSubreddit).get_hot(limit=10)
img_ex = ['.jpg', '.jpeg', '.png', '.gif']

#process all the submissions from the front page
for submission in submissions:
    #it already exists in our folder
    if len(glob.glob('reddit_%s_%s_*' % (targetSubreddit, submission.id))) > 0:
        continue

    if 'http://imgur.com/a/' in submission.url:
        #album submission
        albumId = submission.url[len('http://imgur.com/a/'):]
        htmlSource = requests.get(submission.url).text

        soup = BeautifulSoup(htmlSource)
        matches = soup.select('.album-view-image-link a')
        for match in matches:
            imageUrl = match['href']
            if '?' in imageUrl:
                imageFile = imageUrl[imageUrl.rfind('/') + 1: imageUrl.rfind('?')]
            else:
                imageFile = imageUrl[imageUrl.rfind('/') + 1]
            localFileName = 'reddit_%s_%s_album_%s_imgur_%s' % (targetSubreddit, submission.id, albumId, imageFile)
            downloadImage('http:' + match['href'], localFileName)

    elif "i.imgur.com/" in submission.url:
        #The URL is direct link to the image
        if '?' in submission.url:
            submission.url = submission.url[: submission.url.rfind('?')]
        if "https://" in submission.url:
            localFileName = submission.url[20:]
        if "http://" in submission.url:
            localFileName = submission.url[19:]
        localFileName = 'reddit_%s_%s_album_None_imgur_%s' % (targetSubreddit, submission.id, localFileName)
        downloadImage(submission.url, localFileName)

    elif "http://imgur.com/" in submission.url:
        #single imgurl page with single image
        htmlSource = requests.get(submission.url).text #download the image's page
        soup = BeautifulSoup(htmlSource)
        imageUrl =  'http://'+soup.find('div', attrs={'class':'image textbox'}).img['src'][2:]
        imageFile = imageUrl[imageUrl.rfind('/') + 1:]
        localFileName = 'reddit_%s_%s_album_None_imgur_%s' % (targetSubreddit, submission.id, imageFile)
        
        downloadImage(imageUrl, localFileName)

    elif submission.url[submission.url.rfind('.'):] in img_ex:
        #single static image
        imageFile = submission.url[submission.url.rfind('/') + 1:]
        localFileName = 'reddit_%s_%s_album_None_static_%s' % (targetSubreddit, submission.id, imageFile)
        
        downloadImage(submission.url, localFileName)