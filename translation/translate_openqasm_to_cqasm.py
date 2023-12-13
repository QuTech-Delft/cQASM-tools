from qiskit import QuantumCircuit
import qiskit


def translate(s):
    circuit = QuantumCircuit.from_qasm_str(s)
    circuit = qiskit.compiler.transpile(circuit, basis_gates=['id', 'ry', 'rx', 'cx']) # Modify if needed

    # number_of_qubits = sum(reg.size for reg in circuit.regs if isinstance(reg, qiskit.circuit.QuantumRegister))
    number_of_qubits = circuit.num_qubits

    result = f"version 1.0\n\nqubits {number_of_qubits}\n\n"


    for instruction in circuit.data:
        formatted_qubit_args = [f"q[{circuit.find_bit(q)[0]}]" for q in instruction.qubits]
        joined_formatted_qubit_args = ", ".join(formatted_qubit_args)

        if isinstance(instruction.operation, qiskit.circuit.Measure):
            result += f"measure {joined_formatted_qubit_args}\n"
            continue

        if isinstance(instruction.operation, qiskit.circuit.library.Barrier):
            # Skipped
            continue

        if not isinstance(instruction.operation, qiskit.circuit.Gate):
            raise Exception("Unimplemented")

        gate = instruction.operation

        assert instruction.clbits == tuple()

        gate_name = gate.name

        match gate_name:
            case "h":
                result += f"h {joined_formatted_qubit_args}\n"
            case "id":
                continue
            case "cx":
                result += f"cnot {joined_formatted_qubit_args}\n"
            case "ry":
                result += f"ry {joined_formatted_qubit_args}, {gate.params[0]}\n"
            case "rx":
                result += f"rx {joined_formatted_qubit_args}, {gate.params[0]}\n"
            case _:
                raise Exception("Unknown gate! Add me to the match case")

    return result


test = '''
// Benchmark was created by MQT Bench on 2023-06-29
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: v1.0.0
// Qiskit version: {'qiskit-terra': '0.24.1', 'qiskit-aer': '0.12.0', 'qiskit-ignis': None, 'qiskit-ibmq-provider': '0.20.2', 'qiskit': '0.43.1', 'qiskit-nature': '0.6.2', 'qiskit-finance': '0.3.4', 'qiskit-optimization': '0.5.0', 'qiskit-machine-learning': '0.6.1'}

OPENQASM 2.0;
include "qelib1.inc";
qreg q[4];
qreg qprime[4];

cx q[0], qprime[2];
'''

test2 = '''
// Benchmark was created by MQT Bench on 2023-06-29
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: v1.0.0
// Qiskit version: {'qiskit-terra': '0.24.1', 'qiskit-aer': '0.12.0', 'qiskit-ignis': None, 'qiskit-ibmq-provider': '0.20.2', 'qiskit': '0.43.1', 'qiskit-nature': '0.6.2', 'qiskit-finance': '0.3.4', 'qiskit-optimization': '0.5.0', 'qiskit-machine-learning': '0.6.1'}

OPENQASM 2.0;
include "qelib1.inc";
qreg q[4];
creg meas[4];
u2(pi/2,-0.7167882678555819) q[0];
u1(-1.490342548936602) q[1];
u2(0,0) q[2];
cx q[2],q[1];
ry(-0.4689836211867622) q[1];
ry(-0.4689836211867622) q[2];
cx q[2],q[1];
u2(pi/4,-1.6512501046531909) q[1];
u2(-pi,-pi) q[2];
cx q[2],q[1];
tdg q[1];
u2(4.329343885871547,5.288856933750764) q[3];
cx q[3],q[1];
t q[1];
cx q[2],q[1];
u2(0,3*pi/4) q[1];
u3(pi,-0.3243372398619,0.3243372398619) q[2];
h q[3];
ccx q[0],q[1],q[3];
u2(-pi/2,1.3812349395858394) q[0];
u3(0.0014104532310202874,pi/2,2.677969677273146) q[1];
u3(pi,pi/2,-pi/2) q[3];
cx q[3],q[2];
ry(-0.7103594437025119) q[2];
ry(0.7103594437025119) q[3];
cx q[3],q[2];
u2(-2.0191093047377757,-1.522636840085931) q[2];
u2(-pi,pi/2) q[3];
rzz(2.0971039305177235) q[0],q[3];
rx(-pi/2) q[0];
crx(1.5640163777242566) q[2],q[0];
u1(2.5042812402137704) q[0];
cx q[1],q[0];
ry(-1.0666196369357623) q[0];
ry(-1.0666196369357623) q[1];
cx q[1],q[0];
u1(-2.5042812402137704) q[0];
u2(-pi,-pi) q[1];
u3(pi/4,-pi/2,-pi) q[3];
cx q[2],q[3];
h q[3];
cu1(pi/2) q[2],q[3];
cx q[1],q[2];
cx q[2],q[1];
u1(-1.4624678218563334) q[3];
cu3(3.9824402877397977,0.7203317518888239,1.4645506429344954) q[3],q[0];
barrier q[0],q[1],q[2],q[3];
measure q[0] -> meas[0];
measure q[1] -> meas[1];
measure q[2] -> meas[2];
measure q[3] -> meas[3];
'''

if __name__ == '__main__':
    print(translate(test))

