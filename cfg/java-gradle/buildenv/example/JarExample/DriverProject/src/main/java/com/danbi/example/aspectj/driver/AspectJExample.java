package com.danbi.example.aspectj.driver;

import com.danbi.example.aspectj.library.*;

public class AspectJExample {
    public static void main(String[] args) {
        SaySomething someone = new SaySomething();
        DoSomething somebody = new DoSomething();

        Thread thread = new Thread() {
            public void run() {
                int countSteps = 0;
                for (int i = 0 ; i < 10000000 ; i++)
                    countSteps += i;
                System.out.println("I'm tired. I cannot walk anymore.");
            }
        };

        thread.start();

        somebody.smile();
        someone.sayHello();
        somebody.liftLuggage();
        somebody.showPassport();
        someone.sayBye();
        someone.laugh();
    }
}
