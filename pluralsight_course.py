import json
import urllib.request 
import urllib.parse
from bs4 import BeautifulSoup
import collections
import sys
import os
import fnmatch
from natsort import natsorted, ns
import shutil


def get_html(url):
	req = urllib.request.Request(url)

	try:
	    f = urllib.request.urlopen(req)
	except urllib.error.HTTPError as e:
	    print(e.fp.read())

	response = f.read()

	f.close()

	return response

def course_dict(url):
	response = get_html(url)

	soup = BeautifulSoup(response, "lxml")

	course_accordion = soup.find(id="course_modules__accordion")

	course_dict = collections.OrderedDict()


	for element in course_accordion.find_all('div'):
		x = element.find(class_="accordion-title__title")
		if x :
			course_parent = str(x.get_text())
		else :
			child_list = []
			for child in element.find_all(class_="accordion-content__row") :
				title = child.find(class_="accordion-content__row__title").get_text()
				child_list.append(str(title))

				course_dict[course_parent] = child_list
	
	return course_dict

def main(argv):
	if (len(argv) != 3):
		print("Usage : pluralsight_course.py <url> <input_path> <output_path>")
	else :
		url = argv[0]
		input_path = argv[1]
		output_path = argv[2]

		course = course_dict(url)
		course_count = sum(len(v) for v in course.values())
		
		file_count = len(fnmatch.filter(os.listdir(input_path), '*.mp4'))

		if course_count != file_count :
			return print("File count not match with course list")

		file_list = fnmatch.filter(os.listdir(input_path), '*.mp4')

		file_list = natsorted(file_list)

		i = 0
		for chapter, lessons in course.items():
			chapter_dir = os.path.join(output_path, str(chapter))

			os.mkdir( chapter_dir, mode=0o755 );

			for lesson in lessons :
				shutil.copy2(os.path.join(input_path, file_list[i]), os.path.join(chapter_dir, lesson + ".mp4"))

				i += 1

		print("Done.....")


if __name__ == "__main__":
    main(sys.argv[1:])