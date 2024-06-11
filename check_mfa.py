dict = {
    'email': 'rod@email.com'
}

def func(dict):
    try:
        try:
            var = dict['employeeID']
        except:
            var = "No key found"
        print(f"var: {var}")
        return var
    except Exception as e:
        print(f"An error occurred: {e}")
        # pass

var = func(dict)
print(var)