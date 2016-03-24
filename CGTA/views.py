# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, render, get_object_or_404
from django.template import RequestContext, loader
from django.views import generic
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.core.files import File
from django.utils import timezone
from imagekit import ImageSpec
from imagekit.processors import ResizeToFill
from .models import Document
from .forms import DocumentForm
import cv2, math, os, random, StringIO
import numpy as np
from django.core.files.uploadedfile import InMemoryUploadedFile
#from django.conf import settings
from Website.settings import STATIC_ROOT
try:
    from PIL import Image, ImageOps
except:
    # Mac OSX
    import Image, ImageOps

#views start

def index(request):
	return render(request, 'CGTA/index.html')
	
def about(request):
	return render(request, 'CGTA/about.html')

def docs(request):
	return render(request, 'CGTA/docs.html')
	
#def output(request, image_id):
#	return HttpResponse("This is the CGTA output page.")
	
def upload(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
			initial_file = request.FILES['uploadfile']
			ct_get = form.cleaned_data['class_type']
			#uploaded file to cv2
			cv2_image = cv2.imdecode(np.fromstring(initial_file.read(), np.uint8), 1)
			
			if ct_get == "Output Image (DNN)":
				final_cv2_image = DNNpicture(cv2_image)
			elif ct_get == "Output Image (Bayes)":
				final_cv2_image = BAYESpicture(cv2_image)
			
			#cv2 to pil
			pil_img = Image.fromarray(final_cv2_image)
			
			#pil to file
			img_io = StringIO.StringIO()
			pil_img.save(img_io, format='JPEG')
			final_file = InMemoryUploadedFile(img_io, None, "final_image.jpeg", 'image/jpeg', img_io.len, None)
	
			newdoc = Document(input_image = initial_file, output_image = final_file, class_type = ct_get)
			newdoc.save()
			image = get_object_or_404(Document, pk = newdoc.id)
            # Redirect to the document upload after POST
			#return HttpResponseRedirect(reverse('CGTA.views.output'))
			
			return render(request, 'CGTA/output.html', {'image': image})
    else:
        form = DocumentForm()  # A empty, unbound form

    # Load documents for the upload page
    documents = Document.objects.all()

    # Render upload page with the documents and the form
    return render_to_response(
        'upload.html',
        {'documents': documents, 'form': form},
        context_instance=RequestContext(request)
    )

	

#DNN, CNN, BAYES presentation start
groups = ["N", "B", "C"]
size = 32
border = 2
#gathering theta_DNN

theta_file = open(os.path.join(STATIC_ROOT, "DNN", "theta.txt"))

theta = []

for line in theta_file:
    theta.append(float(line[:len(list(line))]))

theta_file.close

#for Bayesian parameter gathering
means = {}
variances = {}
probs = {}

for group in groups:
	mean_file = open(os.path.join(STATIC_ROOT, "Bayes", "means_%s.txt" % (group)))
	variance_file = open(os.path.join(STATIC_ROOT, "Bayes", "variances_%s.txt" % (group)))
	prob_file = open(os.path.join(STATIC_ROOT, "Bayes", "prob_%s.txt" % (group)))
	means[group] = []
	variances[group] = []
    
	for line in mean_file:
		means[group].append(float(line[:len(list(line))]))
	for line in variance_file:
		variances[group].append(float(line[:len(list(line))]))
	
	probs[group] = float(line[:len(list(line))])

	mean_file.close
	variance_file.close
	prob_file.close
#color source
yellow = np.zeros((32,32, 3), np.uint8)
yellow[:,:] = (255,255,0)

green = np.zeros((32,32, 3), np.uint8)
green[:,:] = (0,128,0)

red = np.zeros((32,32, 3), np.uint8)
red[:,:] = (255,0,0)


def DNNpicture(img):
	green_ctr = 0
	red_ctr = 0
	yellow_ctr = 0
    
	
    #img = cv2.imread("Test/%s.jpeg" % (image))
    
	length = img.shape[0]
	width = img.shape[1]
    
	new_length = length + (length/size - 1) * border
	new_width = width + (width/size - 1) * border
    
	new_image = np.zeros((new_length,new_width, 3), np.uint8)
	new_image[:,:] = (0,0,0)
    
	border_t = 4
    
	#segmented image
	border_image = np.zeros((length + (length/size - 1) * border_t,width + (width/size - 1) * border_t, 3), np.uint8)
	border_image[:,:] = (0,0,0)
    
    
    #with colors
	subregions = segment(img)
    
	for i in range(len(subregions)):
		for j in range(len(subregions["row %d" % (i)])):
            
			border_image[(size+border_t)*i:(size+border_t)*i+size,(size+border_t)*j:(size+border_t)*j+size] = subregions["row %d" % (i)][j]
			
			x_list = feature(subregions["row %d" % (i)][j])
			x = [1]
			
			for color in x_list:
				for number in color:
					x.append(number)
    
			x_vec = [a*b for (a,b) in zip(theta,x)]
			x = sum(x_vec)
			#y_est = 2 / (1 + math.exp(-x))
			
			y_est = random.uniform(0,2)
			if y_est < 0.5:
				new_image[(size+border)*i:(size+border)*i+size,(size+border)*j:(size+border)*j+size] = green
			elif y_est >= 0.5 and y_est < 1.5:
				new_image[(size+border)*i:(size+border)*i+size,(size+border)*j:(size+border)*j+size] = yellow
			else:
				new_image[(size+border)*i:(size+border)*i+size,(size+border)*j:(size+border)*j+size] = red        

	return new_image
	

def BAYESpicture(img):
	length = img.shape[0]
	width = img.shape[1]

	new_length = length + (length/size - 1) * border
	new_width = width + (width/size - 1) * border

	new_image = np.zeros((new_length,new_width, 3), np.uint8)
	new_image[:,:] = (0,0,0)

	border_t = 4

	border_image = np.zeros((length + (length/size - 1) * border_t,width + (width/size - 1) * border_t, 3), np.uint8)
	border_image[:,:] = (255,255,255)
    
    
    #with colors
	subregions = segment(img)
    
	for i in range(len(subregions)):
		for j in range(len(subregions["row %d" % (i)])):
			border_image[(size+border_t)*i:(size+border_t)*i+size,(size+border_t)*j:(size+border_t)*j+size] = subregions["row %d" % (i)][j]
            
			x_list = feature(subregions["row %d" % (i)][j])
              
			BGR_hist = []

			for color_list in x_list:
				for n in color_list:
					BGR_hist.append(n)
            
			p_list = {}
			for group in groups:
				bayes_prob = probs[group]
				for index in range(len(BGR_hist)):
					std_dev = variances[group][index] ** 0.5
					if std_dev == 0:
						pass
					else:
						z_score = (BGR_hist[index] - means[group][index])/ std_dev
						#normal distribution probability to be multiplied with the previous probabilities
						bayes_prob *= 1/(math.sqrt(2*math.pi)*std_dev)*math.exp(-(z_score**2)/2)

				p_list[group] = bayes_prob
            
			group_max = ""
			p_max = 0
			
			for group in groups:    
				if p_list[group] > p_max:
					p_max = p_list[group]
					group_max = group
			
			#y_est = int(random.uniform(0,3))
			#group_max = groups[y_est]
			if group_max == "N":
				new_image[(size+border)*i:(size+border)*i+size,(size+border)*j:(size+border)*j+size] = green
			elif group_max == "B":
				new_image[(size+border)*i:(size+border)*i+size,(size+border)*j:(size+border)*j+size] = yellow
			else:
				new_image[(size+border)*i:(size+border)*i+size,(size+border)*j:(size+border)*j+size] = red
	
	return new_image
	
def segment(img):
    
	size = 32
    #img = cv2.imread(os.path.join(path, image))
    #os.makedirs(path)
    #img = cv2.imread(image)
	length = img.shape[0]
	width = img.shape[1]
    
	rows = int(img.shape[0]/size)
	columns = int(img.shape[1]/size)
	subregions = {}
	for row in range(rows):
		image_list = []
		for column in range(columns):
			new_image = img[(row*size):((row+1)*size),(column*size):((column+1)*size)]
			image_list.append(new_image)
			#cv2.imwrite("%s/sr(%d,%d).jpeg" % (path, row, column), new_image) #where to place subregions
			 
		subregions["row %d" % (row)] = image_list
		
	return subregions
    
def feature(img):
    #img = cv2.imread(image)
    
	length = img.shape[0]
	width = img.shape[1]
	classes = int(math.ceil(math.log(length*width+1,2)))
	class_width = int(math.ceil(255/float(classes)))

	blue_histogram=[0]*classes
	green_histogram=[0]*classes
	red_histogram=[0]*classes

	for row in range(length):
		for column in range(width):
			blue_value = img[row,column,0]
			green_value = img[row,column,1]
			red_value = img[row,column,2]
			
			blue_histogram[int(math.floor(blue_value/float(class_width)))] += 1
			green_histogram[int(math.floor(green_value/float(class_width)))] += 1
			red_histogram[int(math.floor(red_value/float(class_width)))] += 1

			
	return [blue_histogram, green_histogram, red_histogram]





