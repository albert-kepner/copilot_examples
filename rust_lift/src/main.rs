fn main() {
    println!("Hello, the_lift");
    the_lift(&[vec![], vec![], vec![5,5,5],vec![],vec![],vec![],vec![]], 5);
}

fn the_lift(queues: &[Vec<u32>], capacity: u32) -> Vec<u32> {
    let mut lift_state: LiftState = LiftState::new(queues, capacity);
    let mut v: Vec<u32> = vec![];
    while let Some(floor) = lift_state.next_floor() {
        println!("here001: floor = {}", floor);
        v.push(floor);
    }
    v
}

#[derive(Debug)]
enum Direction {
    Up,
    Down,
}

#[derive(Debug)]
struct LiftState {
    direction: Direction,
    capacity: u32,
    floor: u32,
    riders: Vec<u32>,
    queues: Vec<Vec<u32>>,
}

impl LiftState {
    pub fn new(queues: &[Vec<u32>], capacity: u32) -> Self {
        Self {
            direction: Direction::Up,
            capacity: capacity,
            floor: 0,
            riders: vec![],
            queues: queues.iter().cloned().collect(),
        }
    }

    fn next_floor(&mut self) -> Option<u32> {
        println!("here002");
        if let Some(floor) = self.find_next_stop_forward() {
            println!(" ready to stop at {}", floor);
            self.stop_at_floor(floor);
            return Some(floor);
        }
        None
    }

    fn stop_at_floor(&mut self, floor: u32) -> () {

    }

    fn find_next_stop_forward(&self) -> Option<u32> {
        let mut floor = self.floor as usize;
        match self.direction {   
            Direction::Up => {
                while floor < self.queues.len() - 2 {
                    floor += 1;
                    // Count the number of persons queued to go above the
                    // current floor.
                    let mut count_up = 0;
                    let mut count_off = 0;
                    for item in &self.queues[floor] {
                        if *item as usize > floor {
                            count_up += 1;
                        }
                    }
                    for item in &self.riders {
                        if *item as usize == floor {
                            count_off += 1;
                        }
                    }
                    if count_up + count_off > 0 {
                        return Some(floor as u32);
                    }
                }
                None
            }
            Direction::Down => {
                while floor > 0 {
                    floor -= 1;
                    // Count the number of persons queued to go above the
                    // current floor.
                    let mut count_down = 0;
                    let mut count_off = 0;
                    for item in &self.queues[floor] {
                        if (*item as usize) < floor {
                            count_down += 1;
                        }
                    }
                    for item in &self.riders {
                        if *item as usize == floor {
                            count_off += 1;
                        }
                    }
                    if count_down + count_off > 0 {
                        return Some(floor as u32);
                    }
                }
                None
            }
        }
    }
}

// Add your tests here.
// See https://doc.rust-lang.org/stable/rust-by-example/testing/unit_testing.html

#[cfg(test)]
mod tests {
    use super::the_lift;
    
    fn print_queues(queues: &[Vec<u32>], capacity: u32) -> String {
        let mut result = format!("\nLift capacity = {capacity}\n\n Floor    Queue");
        for (i, q) in queues.iter().enumerate().rev() {
            result.push_str(&format!("\n{i:>4} .... {q:?}"));
        }
        result
    }

    fn do_test(queues: &[Vec<u32>], capacity: u32, expected: &[u32]) {
        let actual = the_lift(queues, capacity);
        assert_eq!(actual, expected,
            "\nYour result (left) did not match expected output (right) for the given queues:\n{}\n",
            print_queues(queues, capacity));
    }

    #[test]
    fn test_up() {
        do_test(&[vec![], vec![], vec![5,5,5],vec![],vec![],vec![],vec![]], 5, &[0, 2, 5, 0]);
    }
    // #[test]
    // fn test_down() {
    //     do_test(&[vec![],vec![],vec![1],vec![],vec![],vec![],vec![]], 5, &[0, 2, 1, 0]);
    // }
    // #[test]
    // fn test_up_and_up() {
    //     do_test(&[vec![],vec![3],vec![4],vec![],vec![5],vec![],vec![]], 5, &[0, 1, 2, 3, 4, 5, 0]);
    // }
    // #[test]
    // fn test_down_and_down() {
    //     do_test(&[vec![],vec![0],vec![],vec![],vec![2],vec![3],vec![]], 5, &[0, 5, 4, 3, 2, 1, 0]);
    // }
}
