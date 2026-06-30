#include <stdio.h>

// Ví dụ 2: Tính giai thừa
// Lỗi: Khoá vô tận vì điều kiện sai
int main() {
    int n = 5;
    int fact = 1;
    int i = 1;
    
    // BUG: Điều kiện i <= n sẽ lặp vô tận nếu n = 0
    // vì i sẽ không bao giờ > 0
    while (i < n) {
        fact *= i;
        i++;  // Quên tăng i nếu dùng while
    }
    
    printf("Factorial of %d: %d\n", n, fact);
    return 0;
}

/* SỬA:
for (int i = 1; i <= n; i++) {
    fact *= i;
}
*/
