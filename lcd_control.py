import I2C_LCD_driver
import time
    

def LCD_display_amount_due(amount_due):
    str_amount_due = "$" + str(amount_due)
    myLcd = I2C_LCD_driver.lcd()
    myLcd.lcd_display_string("Amount due: ", 1)
    myLcd.lcd_display_string(str_amount_due, 2)

    if amount_due <= 0:
        myLcd.lcd_clear()
        myLcd.lcd_display_string("Transaction done", 1)

if __name__ == '__main__':
    # test code
    mylcd = I2C_LCD_driver.lcd()
    mylcd.lcd_display_string("Amount due: ", 1)

    counter = 123.45
    while True: 
        message = "$" + str(counter)
        mylcd.lcd_display_string(message, 2)
        counter = counter - 10
        time.sleep(2)