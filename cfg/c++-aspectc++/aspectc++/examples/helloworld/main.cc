#include <iostream>

using namespace std;

void hello() {
    cout << "Hello" << endl;
}

void bye() {
    cout << "bye" << endl;
}

void saySomething(char *message) {
    cout << message << endl;
}

void *inc_x(void *x_void_ptr)
{
    int *x_ptr = (int *)x_void_ptr;
    while (++(*x_ptr) < 100);

    cout << "x increment finished" << endl;

    return NULL;
}

int main(){

    pthread_t inc_x_thread;
    int x;

    if (pthread_create(&inc_x_thread, NULL, inc_x, &x)) {
        cout << "Error creating thread" << endl;
        return 1;
    }

    hello(); //print "Hello"
    bye();
    saySomething("Let's keep in touch!");

    if (pthread_join(inc_x_thread, NULL)) {
        cout << "Error joining thread" << endl;
        return 2;
    }

    return 0;
}
