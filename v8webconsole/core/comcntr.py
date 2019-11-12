import win32com.client
import pythoncom


pythoncom.CoInitialize()
# В зависимости от версии платформы используется V82.COMConnector или V83.COMConnector
V8_COM_CONNECTOR = None
try:
    V8_COM_CONNECTOR = win32com.client.Dispatch("V83.COMConnector")
except pythoncom.com_error:
    V8_COM_CONNECTOR = win32com.client.Dispatch("V82.COMConnector")