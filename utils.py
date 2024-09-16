
# Get the bottom 10% of the data and return the mean
def resting_hr(array_like):
    # print(type(array_like[0]))
    # print(type(array_like))
    if array_like.empty:
        return np.nan # represents "NaN" or "Not a Number"
    # if not isinstance(array_like[0], np.float64):
    #     return np.nan
        
    return array_like[array_like <= np.percentile(array_like, 10)].mean()
            # np.percentile: calculates the 10th percentile (value below which 10% of data falls)of the array
            # array_like <= np.percentile : any elements greater than 10th percentile value, marked as False
            # overall, this selects the elements that are less than or equal to 10th percentile value, and creates a new array with these values. 
            # The average of the elements in the filtered array are taken of the filtered array

# Gets the nearest value in a list of items to the pivot point. Retuns the closest value.
def nearest(items, pivot):
    # Inputs: list of items and pivot point.
    # Ouputs: closest value in list to pivot point.
    return min(items, key=lambda x: abs(x - pivot)) # takes minimum value. Lambda function calcuates absolute difference between each item x in items and the pivot value
