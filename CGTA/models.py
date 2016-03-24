# -*- coding: utf-8 -*-
from django.db import models
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill
from .processors import Grayscale
import cv2

	
class Document(models.Model):
	input_image = models.ImageField(upload_to='input/%Y/%m/%d')
	output_image = models.ImageField(upload_to='output/%Y/%m/%d')
	class_type = models.CharField(max_length = 20)
	
	#output_temp = ImageSpecField(source = 'docfile', format = 'JPEG', options = {'quality': 100})
	#def __str__(self):
		#return self.model_name