# BMI Calculator

def BMI_Cal():
    print("--- BMI Calculator ---")

    # Input validation for weight
    while True:
        try:
            weight = float(input("Enter your weight in kg: "))
            if weight <= 0 or weight >= 200:
                print("Error: Weight must be in range of 200 kg. Please try again.")
                continue
            break
        except ValueError:
            print("Error: Invalid input. Please enter a numeric value for weight.")

    # Input validation for height
    while True:
        try:
            height = float(input("Enter your height in meters (e.g., 1.75): "))
            if height <= 0 or height >= 300:
                print("Error: Height must be in range of 300 cm. Please try again.")
                continue
            break
        except ValueError:
            print("Error: Invalid input. Please enter a numeric value for height.")

    height = height / 100
    BMI = weight / (height * height)
    BMI = round(BMI , 2)
    print("\n--- Results ---")
    print(f'Your body mass index (BMI) is {BMI}')
    if (BMI < 18.5):
        print("Category: Underweight")
    elif(BMI >= 18.5 and BMI <= 24.9):
        print("Category: Normal")
    elif(BMI >= 25 and BMI <= 29.9):
        print("Category: Overweight")
    else:
        print("Category: Obese")

    return "Keep yourself healthy!"

if __name__ == "__main__":
   BMI_Cal()
