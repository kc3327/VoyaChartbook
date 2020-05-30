#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 29 20:00:04 2020

@author: alun
"""

import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime as dt
import time
import yfinance
import statsmodels.api as sm
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, PageBreak, Image, Table, Paragraph
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm


def send_email(receiver_email = "kc3327@columbia.edu, chenkai7@msu.edu"):
    subject = "Three stock chart book"
    body = "This is an email with attachment sent from voya_chartbook.py"
    sender_email = "chenkailunmeme@gmail.com"
#     receiver_email = "kc3327@columbia.edu"
    password = 'Ckl1830506'

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    filename = "ChartBook_Voya.pdf"  # In same directory as script

    # Open PDF file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email    
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)
    # server.quit()
    
def send_email_at(send_time,receiver_email):
    time.sleep(send_time.timestamp() - time.time())
    send_email(receiver_email)



def TimeSeries(msft,spy,tnx,name):
    fig, ax = plt.subplots(figsize=(5,5),constrained_layout=True)
    ax2 = ax.twinx()
    x = msft.index
    y = msft['Close']
    x1 = spy.index
    y1 = spy['Close']
    x2 = tnx.index
    y2 = tnx['Close']
    plt.title("{} Time Series".format(name))
    plt.grid(True)
    ax.set_xlabel("Year")
    ax.set_ylabel("{}/SPY Stock Price".format(name))
    ax.plot(x, y, "b-", linewidth=1.0, label="{} Stock Price".format(name))
    ax.plot(x1, y1, "g-", linewidth=1.0, label="SPY Price")
    ax.legend(loc="upper left", shadow=True)
    sec=ax2.secondary_yaxis('right')
    sec.set_ylabel('10 Year Treasury Yield')
    ax2.plot(x2, y2, "r-", linewidth=1.0, label="10 Year Treasury Yield")
    ax2.legend(loc="upper right", shadow=True)
    fig.savefig("{}_ts.png".format(name))


def MovingAverage(aapl,spy,tnx,name):
    fig,a =  plt.subplots(1,3,figsize=(15,5))
    aapl_ma30=aapl["Close"].rolling(22).mean().dropna()
    aapl_ma180=aapl["Close"].rolling(127).mean().dropna()
    aapl_ma360=aapl["Close"].rolling(255).mean().dropna()
    
    spy_ma30=spy["Close"].rolling(22).mean().dropna()
    spy_ma180=spy["Close"].rolling(127).mean().dropna()
    spy_ma360=spy["Close"].rolling(255).mean().dropna()
    
    tnx_ma30=tnx["Close"].rolling(22).mean().dropna()
    tnx_ma180=tnx["Close"].rolling(127).mean().dropna()
    tnx_ma360=tnx["Close"].rolling(255).mean().dropna()
    
    a[0].set_title("{} Moving Average Stock Price".format(name))
    a[0].set_xlabel("Year")
    a[0].set_ylabel("Moving Average Stock Price")
    a[0].plot(aapl_ma30,label="30 Day Moving Average")
    a[0].plot(aapl_ma180,label="180 Day Moving Average")
    a[0].plot(aapl_ma360,label="360 Day Moving Average")
    a[0].legend(loc="upper left", shadow=True)
    
    a[1].set_title("SPY Moving Average Stock Price")
    a[1].set_xlabel("Year")
    a[1].set_ylabel("Moving Average Stock Price")
    a[1].plot(spy_ma30,label="30 Day Moving Average")
    a[1].plot(spy_ma180,label="180 Day Moving Average")
    a[1].plot(spy_ma360,label="360 Day Moving Average")
    a[1].legend(loc="upper left", shadow=True)
    
    a[2].set_title("TNX Moving Average 10 Year Yield")
    a[2].set_xlabel("Year")
    a[2].set_ylabel("Moving Average Yield")
    a[2].plot(tnx_ma30,label="30 Day Moving Average")
    a[2].plot(tnx_ma180,label="180 Day Moving Average")
    a[2].plot(tnx_ma360,label="360 Day Moving Average")
    a[2].legend(loc="upper left", shadow=True)
    fig.savefig("{}_ma.png".format(name))



def Regression(msft,spy,name,timewindow):
    msft_vs_spy = sm.OLS(msft["Close"][-timewindow:],spy["Close"][-timewindow:]).fit()
    fig,ax = plt.subplots(1,2,figsize=(12,8))
    
    ax[0].set_title("Residual for {}".format(name))
    ax[0].set_xlabel("")
    ax[0].set_ylabel("Residual")
    ax[0].scatter(msft_vs_spy.model.exog[:,0], msft_vs_spy.resid,label="Residual")
    ax[0].legend(loc="upper left", shadow=True)
    ax[0].axhline(y=0)
    ax[1]=sm.graphics.plot_fit(msft_vs_spy, "Close", ax=ax[1])
 
    df_msft_1=msft_vs_spy.summary2().tables[0].values.tolist()
    df_msft_2=msft_vs_spy.summary2().tables[1].values.tolist()
    df_msft_3=msft_vs_spy.summary2().tables[2].values.tolist()
    fig.savefig("{}_{}dayma.png".format(name,timewindow))
    return df_msft_1,df_msft_2,df_msft_3


msft_ = yfinance.Ticker("MSFT")
aapl_ = yfinance.Ticker("AAPL")
tsla_ = yfinance.Ticker("TSLA")
spy_ = yfinance.Ticker("SPY")
tnx_ = yfinance.Ticker("^TNX")
hist_msft=msft_.history(period="max")
hist_aapl=aapl_.history(period="max")
hist_tsla=tsla_.history(period="max")
hist_spy=spy_.history(period="max")
hist_tnx = tnx_.history(period="max")
start_date_forall=max(hist_aapl.index[0],hist_msft.index[0],hist_tsla.index[0],hist_spy.index[0],hist_tnx.index[0])
msft=hist_msft[hist_msft.index>=start_date_forall].copy()
aapl=hist_aapl[hist_aapl.index>=start_date_forall].copy()
tsla=hist_tsla[hist_tsla.index>=start_date_forall].copy()
spy=hist_spy[hist_spy.index>=start_date_forall].copy()
tnx=hist_tnx[hist_tnx.index>=start_date_forall].copy()

TimeSeries(aapl,spy,tnx,'aapl')
TimeSeries(msft,spy,tnx,'msft')
TimeSeries(tsla,spy,tnx,'tsla')

MovingAverage(aapl,spy,tnx,'aapl')
MovingAverage(msft,spy,tnx,'msft')
MovingAverage(tsla,spy,tnx,'tsla')

df_msft_1,df_msft_2,df_msft_3=Regression(msft,spy,"msft",0)
df_msft_1_30,df_msft_2_30,df_msft_3_30=Regression(msft,spy,"msft",30)
df_msft_1_180,df_msft_2_180,df_msft_3_180=Regression(msft,spy,"msft",180)
df_msft_1_30_tnx,df_msft_2_30_tnx,df_msft_3_30_tnx=Regression(msft,tnx,"msfttnx",30)

df_aapl_1,df_aapl_2,df_aapl_3=Regression(aapl,spy,"aapl",0)
df_aapl_1_30,df_aapl_2_30,df_aapl_3_30=Regression(aapl,spy,"aapl",30)
df_aapl_1_180,df_aapl_2_180,df_aapl_3_180=Regression(aapl,spy,"aapl",180)
df_aapl_1_30_tnx,df_aapl_2_30_tnx,df_aapl_3_30_tnx=Regression(aapl,tnx,"aapltnx",30)

df_tsla_1,df_tsla_2,df_tsla_3=Regression(tsla,spy,"tsla",0)
df_tsla_1_30,df_tsla_2_30,df_tsla_3_30=Regression(tsla,spy,"tsla",30)
df_tsla_1_180,df_tsla_2_180,df_tsla_3_180=Regression(tsla,spy,"tsla",180)
df_tsla_1_30_tnx,df_tsla_2_30_tnx,df_tsla_3_30_tnx=Regression(tsla,tnx,"tslatnx",30)

fileName = 'ChartBook_Voya.pdf'

pdf = SimpleDocTemplate(
    fileName,
    pagesize=A4
)
sample_style_sheet = getSampleStyleSheet()
elems = []
elems.append(Paragraph("MSFT",sample_style_sheet['Heading2']))
elems.append(Paragraph("Time Series",sample_style_sheet['Heading4']))
elems.append(Image('msft_ts.png',height=8*cm,width=10*cm))
elems.append(Paragraph("Moving Averages",sample_style_sheet['Heading4']))
elems.append(Image('msft_ma.png',height=5*cm,width=20*cm))
elems.append(Paragraph("Regression, Residuals",sample_style_sheet['Heading4']))
msg="30 Days Window with SPY: The Adjusted R Squared is {}; The number of observation is {}; Coefficient is {} and P value is {}".format(df_msft_1_30[0][-1],df_msft_1_30[3][1],df_msft_2_30[0][0],df_msft_2_30[0][3])
elems.append(Paragraph(msg,sample_style_sheet['Normal']))
elems.append(Image('msft_30dayma.png',height=6*cm,width=12*cm))
msg="180 Days Window with SPY: The Adjusted R Squared is {}; The number of observation is {}; Coefficient is {} and P value is {}".format(df_msft_1_180[0][-1],df_msft_1_180[3][1],df_msft_2_180[0][0],df_msft_2_180[0][3])
elems.append(Paragraph(msg,sample_style_sheet['Normal']))
elems.append(Image('msft_180dayma.png',height=6*cm,width=12*cm))
msg="20 Years Window with SPY: The Adjusted R Squared is {}; The number of observation is {}; Coefficient is {} and P value is {}".format(df_msft_1[0][-1],df_msft_1[3][1],df_msft_2[0][0],df_msft_2[0][3])
elems.append(Paragraph(msg,sample_style_sheet['Normal']))
elems.append(Image('msft_0dayma.png',height=6*cm,width=12*cm))
msg="30 Days Window with TNX: The Adjusted R Squared is {}; The number of observation is {}; Coefficient is {} and P value is {}".format(df_msft_1_30_tnx[0][-1],df_msft_1_30_tnx[3][1],df_msft_2_30_tnx[0][0],df_msft_2_30_tnx[0][3])
elems.append(Paragraph(msg,sample_style_sheet['Normal']))
elems.append(Image('msfttnx_30dayma.png',height=6*cm,width=12*cm))


elems.append(PageBreak())

elems.append(Paragraph("AAPL",sample_style_sheet['Heading2']))
elems.append(Paragraph("Time Series",sample_style_sheet['Heading4']))
elems.append(Image('aapl_ts.png',height=8*cm,width=10*cm))
elems.append(Paragraph("Moving Averages",sample_style_sheet['Heading4']))
elems.append(Image('aapl_ma.png',height=5*cm,width=20*cm))
elems.append(Paragraph("Regression, Residuals",sample_style_sheet['Heading4']))
msg="30 Days Window with SPY: The Adjusted R Squared is {}; The number of observation is {}; Coefficient is {} and P value is {}".format(df_aapl_1_30[0][-1],df_aapl_1_30[3][1],df_aapl_2_30[0][0],df_aapl_2_30[0][3])
elems.append(Paragraph(msg,sample_style_sheet['Normal']))
elems.append(Image('aapl_30dayma.png',height=6*cm,width=12*cm))
msg="180 Days Window with SPY: The Adjusted R Squared is {}; The number of observation is {}; Coefficient is {} and P value is {}".format(df_aapl_1_180[0][-1],df_aapl_1_180[3][1],df_aapl_2_180[0][0],df_aapl_2_180[0][3])
elems.append(Paragraph(msg,sample_style_sheet['Normal']))
elems.append(Image('aapl_180dayma.png',height=6*cm,width=12*cm))
msg="20 Years Window with SPY: The Adjusted R Squared is {}; The number of observation is {}; Coefficient is {} and P value is {}".format(df_aapl_1[0][-1],df_aapl_1[3][1],df_aapl_2[0][0],df_aapl_2[0][3])
elems.append(Paragraph(msg,sample_style_sheet['Normal']))
elems.append(Image('aapl_0dayma.png',height=6*cm,width=12*cm))
msg="30 Days Window with TNX: The Adjusted R Squared is {}; The number of observation is {}; Coefficient is {} and P value is {}".format(df_aapl_1_30_tnx[0][-1],df_aapl_1_30_tnx[3][1],df_aapl_2_30_tnx[0][0],df_aapl_2_30_tnx[0][3])
elems.append(Paragraph(msg,sample_style_sheet['Normal']))
elems.append(Image('aapltnx_30dayma.png',height=6*cm,width=12*cm))

elems.append(PageBreak())

elems.append(Paragraph("TSLA",sample_style_sheet['Heading2']))
elems.append(Paragraph("Time Series",sample_style_sheet['Heading4']))
elems.append(Image('tsla_ts.png',height=8*cm,width=10*cm))
elems.append(Paragraph("Moving Averages",sample_style_sheet['Heading4']))
elems.append(Image('tsla_ma.png',height=5*cm,width=20*cm))
elems.append(Paragraph("Regression, Residuals",sample_style_sheet['Heading4']))
msg="30 Days Window with SPY: The Adjusted R Squared is {}; The number of observation is {}; Coefficient is {} and P value is {}".format(df_tsla_1_30[0][-1],df_tsla_1_30[3][1],df_tsla_2_30[0][0],df_tsla_2_30[0][3])
elems.append(Paragraph(msg,sample_style_sheet['Normal']))
elems.append(Image('tsla_30dayma.png',height=6*cm,width=12*cm))
msg="180 Days Window with SPY: The Adjusted R Squared is {}; The number of observation is {}; Coefficient is {} and P value is {}".format(df_tsla_1_180[0][-1],df_tsla_1_180[3][1],df_tsla_2_180[0][0],df_tsla_2_180[0][3])
elems.append(Paragraph(msg,sample_style_sheet['Normal']))
elems.append(Image('tsla_180dayma.png',height=6*cm,width=12*cm))
msg="20 Years Window with SPY: The Adjusted R Squared is {}; The number of observation is {}; Coefficient is {} and P value is {}".format(df_tsla_1[0][-1],df_tsla_1[3][1],df_tsla_2[0][0],df_tsla_2[0][3])
elems.append(Paragraph(msg,sample_style_sheet['Normal']))
elems.append(Image('tsla_0dayma.png',height=6*cm,width=12*cm))
msg="30 Days Window with TNX: The Adjusted R Squared is {}; The number of observation is {}; Coefficient is {} and P value is {}".format(df_tsla_1_30_tnx[0][-1],df_tsla_1_30_tnx[3][1],df_tsla_2_30_tnx[0][0],df_tsla_2_30_tnx[0][3])
elems.append(Paragraph(msg,sample_style_sheet['Normal']))
elems.append(Image('tslatnx_30dayma.png',height=6*cm,width=12*cm))
pdf.build(elems)

receiver_email = "kc3327@columbia.edu, chenkai7@msu.edu"   
first_email_time = dt.datetime.now() + dt.timedelta(seconds=10)
interval = dt.timedelta(days=1) # set the interval
send_time = first_email_time
while True:
    send_email_at(send_time,receiver_email)
    send_time = send_time + interval