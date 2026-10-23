# BMI Calculator

def BMI_Cal(w,h):
    h = h / 100
    BMI = w / (h * h)
    BMI = round(BMI , 2)
    print(f'Your body mass index (BMI) is {BMI}')
    if (BMI < 18.5):
        print("You are underweight")
    elif(BMI >= 18.5 and BMI <= 24.9):
        print("Your body mass index is normal")
    elif(BMI >= 25 and BMI <= 29.9):
        print("You are overweight")
    else:
        print("Your body mass is high that may impair health")

    return "Keep yourself healthy!"

height = float(input("Enter your height in cm: \n"))
weight = float(input("Enter your weight in kg: \n"))

Bmi = BMI_Cal(weight,height)
print(Bmi)
    