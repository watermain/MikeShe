import ctypes

lib = ctypes.CDLL(r"C:\Work\Main\Products\bin\x64\MShe_wmd.dll", winmode=0)

#---------------------------------------------------

lib.MSHEWM_GETELEMENTCOUNT.argtypes = [
  ctypes.c_char_p,
  ctypes.POINTER(ctypes.c_int),
  ctypes.c_size_t
]
lib.MSHEWM_GETELEMENTCOUNT.restype = ctypes.c_int

def get_element_count(element_set_id):
  elementSetId = element_set_id.encode()  
  str_len = ctypes.c_size_t(len(elementSetId))
  elementCount = ctypes.c_int(0)
  res = lib.MSHEWM_GETELEMENTCOUNT(elementSetId, ctypes.byref(elementCount), str_len)
  return elementCount.value

#---------------------------------------------------

lib.MSHEWM_GETVALUES.argtypes = [
  ctypes.c_char_p,
  ctypes.c_char_p,
  ctypes.POINTER(ctypes.c_int),
  ctypes.POINTER(ctypes.c_double),
  ctypes.POINTER(ctypes.c_double),
  ctypes.POINTER(ctypes.c_double),
  ctypes.c_size_t,
  ctypes.c_size_t
]
lib.MSHEWM_GETVALUES.restype = ctypes.c_int

def get_values(quantity_ID, element_set_id):
  quantityID = quantity_ID.encode()
  q_len = ctypes.c_size_t(len(quantityID))
  elementSetID = element_set_id.encode()
  e_len = ctypes.c_size_t(len(elementSetID))
  n_elements = get_element_count(element_set_id)
  n = ctypes.c_int(n_elements)
  startTime = ctypes.c_double(0)
  endTime = ctypes.c_double(0)
  values_c = (ctypes.c_double * n_elements)()
  res = lib.MSHEWM_GETVALUES(
    quantityID, elementSetID, 
    ctypes.byref(n), ctypes.byref(startTime), ctypes.byref(endTime), values_c,
    q_len, e_len)
  return startTime.value, endTime.value, values_c[:]

#---------------------------------------------------