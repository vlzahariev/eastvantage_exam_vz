# eastvantage_exam_vz

This repo contain the code of the task for the exam.

Once you get the code you need to install (if not yet) all the packages/libraries I used so the app can work properly.

To execute the app you need to navigate to the folder 
where the project is if you are not there already. In my case it is:
    " cd  C:\Users\vlzah\PycharmProjects\eastvamtage_exam_vz> "



The command which will start uvicorn as a local server is:
    " uvicorn main:app --reload "
    main is the name of the file, app is the name of the app (app = FastApi()), 
and reload is using in order to refresh the visualisation in the browser 
when something get changed in the code