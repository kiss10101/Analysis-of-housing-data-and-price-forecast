@echo off
title ��Դ���ݷ�����۸�Ԥ��ϵͳ������
echo ����������Դ���ݷ�����۸�Ԥ��ϵͳ...
echo.

REM ������⻷��
if exist .venv\Scripts\activate.bat (
    echo ���ڼ������⻷��...
    call .venv\Scripts\activate.bat
) else (
    echo ����: δ�ҵ����⻷��������ʹ��ϵͳPython����
)

REM ��������Ƿ��Ѱ�װ
echo ���ڼ������...
python -m pip install -r requirements.txt 2>nul

REM ������ݿ��Ƿ���ҪǨ��
echo ���ڼ�����ݿ�Ǩ��...
python manage.py migrate

REM ����������
echo.
echo ��������Web������...
echo.
echo ϵͳ�������������: http://127.0.0.1:8000/app/login/
echo ��Ctrl+C����ֹͣ������
echo.

REM �Զ��������
start http://127.0.0.1:8000/app/login/

REM ����Django������
python manage.py runserver 0.0.0.0:8000 