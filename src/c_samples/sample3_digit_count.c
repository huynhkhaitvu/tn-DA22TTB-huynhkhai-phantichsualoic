#include <stdio.h>

// Ví dụ 3: Đếm các chữ số 1 trong một số
// Lỗi: Logic đếm sai
int main() {
    int num = 111;
    int count = 0;
    
    // BUG: Chia cho 10 nhưng không kiểm tra chữ số cuối
    while (num > 0) {
        // Kiểm tra xem chữ số cuối có phải là 1 không
        if (num % 10 != 1) {  // BUG: Nên là == 1, không phải != 1
            count++;
        }
        num /= 10;
    }
    
    printf("Count of 1s: %d\n", count);
    return 0;
}

/* SỬA:
if (num % 10 == 1) {
    count++;
}
*/
