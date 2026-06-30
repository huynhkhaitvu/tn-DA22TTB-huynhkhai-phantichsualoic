#include <stdio.h>

// Ví dụ 1: Tính tổng các số từ 1 đến n
// Lỗi: Vòng lặp sai điều kiện
int main() {
    int n = 5;
    int sum = 0;
    
    // BUG: Điều kiện i < n nên i sẽ là 0, 1, 2, 3, 4
    // Nhưng chúng ta muốn 1, 2, 3, 4, 5
    for (int i = 1; i < n; i++) {
        sum += i;
    }
    
    printf("Sum: %d\n", sum);  // Sai kết quả
    return 0;
}

/* SỬA:
for (int i = 1; i <= n; i++) {  // Đổi < thành <=
    sum += i;
}
*/
