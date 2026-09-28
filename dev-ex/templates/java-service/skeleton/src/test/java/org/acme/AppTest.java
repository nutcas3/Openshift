package org.acme;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class AppTest {

    @Test
    void greetingReturnsName() {
        assertEquals("Hello from ${{ values.name }}\n", App.greeting());
    }
}
